import base64
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

import aiohttp
import requests
from app.services.payment_systems.main_interface import PaymentSystemInterface
from app.logger import get_logger

logger = get_logger()


class PayginePaymentSystemService(PaymentSystemInterface):
    def __init__(self):
        self.PAYGINE_SECTOR = None
        self.PAYGINE_SIGN_PASSWORD = None
        self.PAYGINE_BASE_URL = "https://pay.paygine.com"

    def _make_signature(self, *values) -> str:
        """
        Цифровая подпись (Приложение №2):
        str = sector + amount + currency + password
        sig = base64( sha256(str).hexdigest() )
        """
        raw = "".join(str(v) for v in values)
        sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return base64.b64encode(sha.encode("ascii")).decode("ascii")

    def _register_order(self, amount: int, currency: int, description: str, reference: str) -> Optional[str]:
        """
        POST /webapi/Register — регистрирует заказ, возвращает ID заказа.
        amount передаётся в копейках.
        """
        sig = self._make_signature(
            self.PAYGINE_SECTOR, amount, currency, self.PAYGINE_SIGN_PASSWORD)
        payload = {
            "sector": self.PAYGINE_SECTOR,
            "amount": amount,
            "currency": currency,
            "description": description,
            "reference": reference,
            "signature": sig,
        }
        resp = requests.post(
            f"{self.PAYGINE_BASE_URL}/webapi/Register",
            data=payload,
            timeout=30,
        )
        try:
            root = ET.fromstring(resp.text)
            data = {child.tag: (child.text or "").strip() for child in root}
        except ET.ParseError:
            return None

        if "code" in data:
            return None

        return data.get("id")

    def create_link(
        self,
        final_amount: Decimal,
        user_email: str,
        description: Optional[str],
        payment_id: str,
        operation_id: str = "",
        is_subscription: bool = False,
        nomenclature=None,
    ) -> str:
        """
        Регистрирует заказ в Paygine и возвращает ссылку на оплату.
        final_amount — сумма в рублях (Decimal), конвертируется в копейки.
        """
        amount_kopecks = int(final_amount * 100)
        currency = 643  # RUB

        reference = f"{operation_id or payment_id}-{datetime.now().strftime('%H%M%S%f')}"
        order_id = self._register_order(
            amount=amount_kopecks,
            currency=currency,
            description=description,
            reference=reference,
        )
        if not order_id:
            return ""

        sig = self._make_signature(
            self.PAYGINE_SECTOR, order_id, self.PAYGINE_SIGN_PASSWORD)
        return (
            f"{self.PAYGINE_BASE_URL}/webapi/Purchase"
            f"?sector={self.PAYGINE_SECTOR}&id={order_id}&signature={sig}",
            order_id
        )

    def _verify_xml_signature(self, xml_str: str) -> bool:
        """
        Приложение №2: подпись считается по значениям ВСЕХ тегов XML
        в порядке их следования (кроме <signature>), затем пароль.
        Набор полей не фиксирован — берём динамически из сырого XML.
        """
        root = ET.fromstring(xml_str)
        values = [(child.tag, (child.text or "").strip()) for child in root if child.tag != "signature"]
        received_sig = (root.findtext("signature") or "").strip()
        raw = "".join(v for _, v in values) + self.PAYGINE_SIGN_PASSWORD
        sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        expected_sig = base64.b64encode(sha.encode("ascii")).decode("ascii")
        return expected_sig == received_sig

    def check_payment(self, _operation, payload) -> Optional[str]:
        """
        Проверяет подпись входящего колбэка от Paygine.
        payload["raw_xml"] — сырая строка XML для точной проверки подписи.
        """
        raw_xml = payload.get("raw_xml", "")
        if raw_xml and not self._verify_xml_signature(raw_xml):
            return "The signatures don't match"
        return None

    def prepare_payload(self, payload: str) -> dict:
        """
        Парсит XML-тело колбэка от Paygine в унифицированный словарь.

        Пример XML:
            <operation>
                <order_id>12332974</order_id>       ← ID заказа в Paygine
                <reference>uuid-timestamp</reference> ← наш operation_id + суффикс
                <id>4331530</id>                    ← ID транзакции
                <state>APPROVED</state>
                <fee>0</fee>                        ← в копейках
                <signature>...</signature>
            </operation>
        """
        from app.enums import OrderStatusChoices
        print(f"payload type: {type(payload)}")
        print(f"payload: {payload}")
        root = ET.fromstring(payload)
        data = {child.tag: (child.text or "").strip() for child in root}

        reference = data.get("reference", "")
        # reference формировали как "{operation_id}-{HHMMSSffffff}" в create_link
        # operation_id — это UUID (36 символов), берём его напрямую
        operation_id = reference[:36] if len(reference) >= 36 else reference

        fee_kopecks = int(data.get("fee", 0) or 0)
        status = ""
        if data.get("order_state") == "CANCELED" and data.get("state") == "APPROVED" and data.get("type") == "REVERSE":
            status = OrderStatusChoices.REFUNED
        if data.get("order_state") == "COMPLETED" and data.get("state") == "APPROVED" and data.get("type") == "REVERSE":
            status = OrderStatusChoices.PARTIALLY_REFUNDED
        elif data.get("order_state") == "COMPLETED" and data.get("state") == "APPROVED" and data.get("type") == "PURCHASE":
            status = OrderStatusChoices.PAID
        elif data.get("order_state") == "REGISTERED" and data.get("state") == "REJECTED" and data.get("type") == "PURCHASE":
            status = OrderStatusChoices.REJECTED
        elif data.get("order_state") == "REGISTERED" and data.get("state") == "ERROR" and data.get("type") == "PURCHASE":
            status = OrderStatusChoices.ERROR
        elif data.get("order_state") == "REGISTERED" and data.get("state") == "TIMEOUT" and data.get("type") == "PURCHASE":
            status = OrderStatusChoices.UNKNOWN
        elif data.get("order_state") == "EXPIRED":
            status = OrderStatusChoices.EXPIRED
        return {
            "payment_dt": datetime.now(),
            "status": status,
            "fee": fee_kopecks / 100,
            "invoice_id": data.get("order_id", ""),
            "receipt_link": "",
            "crc": data.get("approval_code", ""),
            "operation_id": operation_id,
            "addtional_fields": {
                "order_id": data.get("order_id", ""),
                "transaction_id": data.get("id", ""),
                "signature": data.get("signature", ""),
                "state": data.get("state", ""),
                "order_state": data.get("order_state", ""),
            },
        }

    def get_nomenclature(self, base_sno, base_nds, base_items: List[dict]) -> Optional[dict]:
        """Paygine не поддерживает фискализацию через этот интерфейс — возвращаем None."""
        return None
    
    async def refund(self, order, amount):
        CURRENCY_MAP = {
            'RUB': 643,
            'USD': 840,
            'EUR': 978
        }     
        sig = self._make_signature(
            self.PAYGINE_SECTOR, 
            order.payment_system_order_id, 
            amount,
            CURRENCY_MAP[order.currency],
            self.PAYGINE_SIGN_PASSWORD
        )
        payload = {
            "sector": self.PAYGINE_SECTOR,
            "id": order.payment_system_order_id,
            "amount": amount,
            "currency": CURRENCY_MAP[order.currency],
            "signature": sig,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.PAYGINE_BASE_URL}/webapi/Reverse",
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    body = await response.text()
                try:
                    root = ET.fromstring(body)
                    data = {child.tag: (child.text or "").strip() for child in root}
                    print(f"Response {data=}")
                    return data["id"]
                except ET.ParseError as exc:
                    logger.error(f"Ошибка: {type(exc)} - {exc}")
                    raise Exception(f"Ошибка: {type(exc)} - {exc}")
                except KeyError as exc:
                    raise Exception(f"Ошибка: {type(exc)} - {exc}, {data=}")
        except aiohttp.ClientError as exc:
            logger.error(f"Ошибка соединения с PAYGINE: {exc}")
            raise Exception(
                f"Ошибка соединения с PAYGINE: {exc}"
            ) from exc

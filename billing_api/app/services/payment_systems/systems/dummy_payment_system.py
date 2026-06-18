import json
from datetime import datetime
from typing import List, Optional
from urllib import parse

from app.services.payment_systems.main_interface import PaymentSystemInterface


class DummyPaymentSystemService(PaymentSystemInterface):

    def __init__(self):
        self.HOST = None

    def create_link(self, final_amount, user_email, description, payment_id, operation_id=0, is_subscription=False, nomenclature=None) -> str:
        """Creates link for the given user's payment"""
        return self._generate_link(
            operation_id=operation_id,
            value=final_amount,
            user_email=user_email,
            description=description,
        )

    def check_payment(self, operation, payload) -> Optional[str]:
        """Dummy всегда подтверждает оплату (тестовая платёжная система)."""
        return None

    def prepare_payload(self, payload):
        """Разбирает тело dummy-колбэка в единый формат для payment_callback."""
        if isinstance(payload, (bytes, bytearray)):
            payload = payload.decode()
        if isinstance(payload, str):
            parsed = dict(parse.parse_qsl(payload))
            if not parsed:
                parsed = json.loads(payload) if payload else {}
        else:
            parsed = payload
        return {
            "payment_dt": datetime.now(),
            "status": 3,  # OrderStatusChoices.PAID — хардкод во избежание циклического импорта
            "fee": 0,
            "invoice_id": parsed.get("operation_id", ""),
            "receipt_link": "",
            "crc": "",
            "operation_id": parsed.get("operation_id"),
            "addtional_fields": {},
        }

    def get_nomenclature(self, base_sno, base_nds, base_items: List[dict]) -> Optional[dict]:
        """Get nomenclature"""
        items = [
            dict(
                name=item.get("name"),
                quantity=item.get("count"),
                sum=float(item.get("amount")),
                tax=base_nds,
                cost=float(item.get("cost")),
            ) for item in base_items
        ]
        nomenclature = {
            "sno": base_sno,
            "items": items,
        }
        return nomenclature

    def _generate_link(self, operation_id: str, value: float, user_email: str, description: str) -> str:
        query = parse.urlencode({
            "operation_id": operation_id,
            "sum": value,
            "email": user_email or "",
            "description": description or "",
        })
        return "https://%(host)s/api/v1/dummy-payment/?%(query)s" % {
            "host": self.HOST,
            "query": query,
        }

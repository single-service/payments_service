import decimal
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from urllib import parse

from app.services.payment_systems.main_interface import PaymentSystemInterface

# from django.conf import settings
# from rest_framework.request import Request


ROBOKASSA_SNO_MAP = {
    1: "osn",
    2: "usn_income",
    3: "usn_income_outcome",
    4: "esn",
    5: "patent",
}

ROBOKASSA_TAX_MAP = {
    1: "none",
    2: "vat0",
    3: "vat10",
    4: "vat110",
    5: "vat20",
    7: "vat120",
    8: "vat5",
    9: "vat7",
    10: "vat105",
    11: "vat107",
}


class RobokassaPaymentSystemService(PaymentSystemInterface):
    def __init__(self):
        self.ROBOKASSA_PASSWORD_1 = None,  # settings.ROBOKASSA_PASSWORD_1
        self.ROBOKASSA_PASSWORD_2 = None,  # settings.ROBOKASSA_PASSWORD_2
        self.ROBOKASSA_LOGIN = None,  # settings.ROBOKASSA_LOGIN
        self.ROBOKASSA_TEST = None,  # settings.ROBOKASSA_TEST
        self.robokassa_payment_url = 'https://auth.robokassa.ru/Merchant/Index.aspx'

    def _parse_response(self, request: str) -> dict:
        """
        :param request: Link.
        :return: Dictionary.
        """
        params = {}

        for item in request.split('&'):
            key, value = item.split('=')
            params[key] = value
        return params

    def _calculate_signature(self, *args) -> str:
        """Create signature MD5."""
        return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()

    def _check_signature_result(
        self,
        order_number: int,  # invoice number
        received_sum: decimal.Decimal,  # cost of goods, RU
        received_signature: str,  # SignatureValue
        password: str,
        **kwargs  # Additional parameters with 'Shp_' prefix
    ) -> bool:
        signature_args = [received_sum, order_number, password]

        # Добавляем отсортированные дополнительные параметры
        sorted_kwargs = sorted(kwargs.items())
        for key, value in sorted_kwargs:
            signature_args.append(f"{key}={value}")

        signature = self._calculate_signature(*signature_args)

        return signature.lower() == received_signature.lower()

    def create_link(self, final_amount, user_email, description, payment_id, operation_id=0, is_subscription=False, nomenclature=None) -> str:
        signature_args = [self.ROBOKASSA_LOGIN, final_amount, ""]
        if nomenclature:
            signature_args.append(json.dumps(nomenclature))
        signature_args += [self.ROBOKASSA_PASSWORD_1,
                           f"Shp_operation_id={operation_id}", f"Shp_user_payment_id={payment_id}"]
        signature = self._calculate_signature(*signature_args)
        self.ROBOKASSA_TEST = 1 if str(self.ROBOKASSA_TEST) == "1" else 0

        data = {
            'MerchantLogin': self.ROBOKASSA_LOGIN,
            'OutSum': final_amount,
            'InvId': "",
            'Description': description,
            'SignatureValue': signature,
            'IsTest': self.ROBOKASSA_TEST,
            'Shp_operation_id': operation_id,
            'Shp_user_payment_id': payment_id,
            'Recurring': "true" if is_subscription else "false",
        }
        if user_email:
            data['Email'] = user_email
        if nomenclature:
            data['Receipt'] = json.dumps(nomenclature)
        return f'{self.robokassa_payment_url}?{parse.urlencode(data)}'

    def check_payment(self, operation, payload) -> Tuple[Optional[dict], Optional[str]]:
        """Verification of notification (ResultURL).
        :param request: HTTP parameters.
        """
        print("type(operation.final_price):", type(operation.final_price))
        print("type(payload.OutSum):", type(Decimal(payload["addtional_fields"]["OutSum"])))

        is_valid_signature = self._check_signature_result(
            payload["invoice_id"],
            payload["addtional_fields"]["OutSum"],
            payload["addtional_fields"]["SignatureValue"],
            self.ROBOKASSA_PASSWORD_2,
            Shp_operation_id=payload["operation_id"],
            Shp_user_payment_id=payload["addtional_fields"]["Shp_user_payment_id"],
            # Дополнительный параметр
        )

        if not is_valid_signature:
            return "The signatures don't match"

        return None

    def prepare_payload(self, payload):
        param_request = self._parse_response(payload)
        return {
            "payment_dt": datetime.now(),
            "status": 3,
            "fee": float(param_request.get('Fee')) if param_request.get('Fee') else 0,
            "invoice_id": param_request['InvId'],
            "receipt_link": "",
            "crc": param_request['crc'],
            "operation_id": param_request['Shp_operation_id'],
            "addtional_fields": {
                "SignatureValue": param_request['SignatureValue'],
                "OutSum": param_request['OutSum'],
                "Shp_user_payment_id": param_request["Shp_user_payment_id"]
            }
        }

    def get_nomenclature(self, base_sno, base_nds, base_items: List[dict]) -> Tuple[Optional[dict], Optional[str]]:
        """Get nomenclature"""
        sno = ROBOKASSA_SNO_MAP.get(base_sno)
        tax = ROBOKASSA_TAX_MAP.get(base_nds)
        items = [
            dict(
                name=item.get("name"),
                quantity=item.get("count"),
                sum=float(item.get("amount")),
                tax=tax,
                cost=float(item.get("cost"))
            ) for item in base_items
        ]
        nomenclature = {
            "sno": sno,
            "items": items
        }
        return nomenclature

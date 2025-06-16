import decimal
import hashlib
from urllib import parse
from typing import Any, Dict, Optional, Tuple
import random
from decimal import Decimal
from datetime import datetime

# from django.conf import settings
# from rest_framework.request import Request

# from billing.models import UserPayment
# from billing.payment_systems.main_interface import PaymentSystemInterface
from app.services.payment_systems.main_interface import PaymentSystemInterface
from app.services.operations_service import OperationsService


class RobokassaPaymentSystemService(PaymentSystemInterface):
    def __init__(self):
        self.ROBOKASSA_PASSWORD_1 = None, # settings.ROBOKASSA_PASSWORD_1
        self.ROBOKASSA_PASSWORD_2 = None, # settings.ROBOKASSA_PASSWORD_2
        self.ROBOKASSA_LOGIN = None, # settings.ROBOKASSA_LOGIN
        self.ROBOKASSA_TEST = None, # settings.ROBOKASSA_TEST
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
    

    def create_link(self, final_amount, user_email, description, payment_id, operation_id=0, is_subscription=False) -> str:
        signature = self._calculate_signature(
            self.ROBOKASSA_LOGIN,
            final_amount,
            "",
            self.ROBOKASSA_PASSWORD_1,
            f"Shp_operation_id={operation_id}",
            f"Shp_user_payment_id={payment_id}",
        )
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
            'Email': user_email,
            'Recurring': "true" if is_subscription else "false",
        }
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
            "receipt_link":"",
            "crc": param_request['crc'],
            "operation_id": param_request['Shp_operation_id'],
            "addtional_fields": {
                "SignatureValue": param_request['SignatureValue'],
                "OutSum": param_request['OutSum'],
                "Shp_user_payment_id": param_request["Shp_user_payment_id"]
            }
        }

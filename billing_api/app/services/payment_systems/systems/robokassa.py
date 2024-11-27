import decimal
import hashlib
from urllib import parse
from typing import Any, Dict, Optional, Tuple

# from django.conf import settings
# from rest_framework.request import Request

# from billing.models import UserPayment
# from billing.payment_systems.main_interface import PaymentSystemInterface
from app.services.payment_systems.main_interface import PaymentSystemInterface


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

        for item in parse.urlparse(request).query.split('&'):
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

    def create_link(self, final_amount, user_email, description, payment_id, invoice_id=0) -> str:
        signature = self._calculate_signature(
            self.ROBOKASSA_LOGIN,
            final_amount,
            invoice_id,
            self.ROBOKASSA_PASSWORD_1,
            f"Shp_user_payment_id={payment_id}",
        )
        self.ROBOKASSA_TEST = 1 if str(self.ROBOKASSA_TEST) == "1" else 0

        data = {
            'MerchantLogin': self.ROBOKASSA_LOGIN,
            'OutSum': final_amount,
            'InvId': invoice_id,
            'Description': description,
            'SignatureValue': signature,
            'IsTest': self.ROBOKASSA_TEST,
            'Shp_user_payment_id': payment_id,
            'Email': user_email
        }
        return f'{self.robokassa_payment_url}?{parse.urlencode(data)}'

    def check_payment(self, request) -> Tuple[Optional[dict], Optional[str]]:
        """Verification of notification (ResultURL).
        :param request: HTTP parameters.
        """

        param_request = self._parse_response(request.get_full_path())
        cost = param_request['OutSum']
        payment_id = param_request['InvId']
        fee = param_request.get('Fee') if param_request.get('Fee') else 0
        signature = param_request['SignatureValue']
        user_payment_id = param_request['Shp_user_payment_id']

        # user_payment = UserPayment.objects.select_related('payment_method', 'user').filter(id=user_payment_id).first()
        # if not user_payment:
        #     return None, "UserPayment not found"

        is_valid_signature = self._check_signature_result(
            payment_id,
            cost,
            signature,
            self.pass2,
            Shp_user_payment_id=user_payment_id,  # Дополнительный параметр
        )
        data = {
            # "user_payment": user_payment,
            "payment_id": payment_id,
            "sum": cost,
            "fee": fee
        }

        if not is_valid_signature:
            return data, "The signatures don't match"

        return data, None

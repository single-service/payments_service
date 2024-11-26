import decimal
import hashlib
from urllib import parse
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from rest_framework.request import Request

from billing.models import UserPayment
from billing.payment_systems.main_interface import PaymentSystemInterface
from users.models import User


class PaymentSystemService(PaymentSystemInterface):
    def __init__(self):
        self.pass1 = settings.ROBOKASSA_PASSWORD_1
        self.pass2 = settings.ROBOKASSA_PASSWORD_2
        self.login = settings.ROBOKASSA_LOGIN
        self.test = settings.ROBOKASSA_TEST
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

    def create_link(self, payment_data: Dict[str, Any], purchaser: User, user_payment: UserPayment) -> str:
        signature = self._calculate_signature(
            self.login,
            payment_data['total_amount'],
            0,
            self.pass1,
            f"Shp_user_payment_id={user_payment.id}",
        )

        data = {
            'MerchantLogin': self.login,
            'OutSum': payment_data['total_amount'],
            'InvId': 0,
            'Description': user_payment.expense.name_ru,
            'SignatureValue': signature,
            'IsTest': self.test,
            'Shp_user_payment_id': user_payment.id,
            'Email': purchaser.email
        }
        return f'{self.robokassa_payment_url}?{parse.urlencode(data)}'

    def check_payment(self, request: Request) -> Tuple[Optional[dict], Optional[str]]:
        """Verification of notification (ResultURL).
        :param request: HTTP parameters.
        """

        param_request = self._parse_response(request.get_full_path())
        cost = param_request['OutSum']
        payment_id = param_request['InvId']
        fee = param_request.get('Fee') if param_request.get('Fee') else 0
        signature = param_request['SignatureValue']
        user_payment_id = param_request['Shp_user_payment_id']

        user_payment = UserPayment.objects.select_related('payment_method', 'user').filter(id=user_payment_id).first()
        if not user_payment:
            return None, "UserPayment not found"

        is_valid_signature = self._check_signature_result(
            payment_id,
            cost,
            signature,
            self.pass2,
            Shp_user_payment_id=user_payment_id,  # Дополнительный параметр
        )
        data = {
            "user_payment": user_payment,
            "payment_id": payment_id,
            "sum": cost,
            "fee": fee
        }

        if not is_valid_signature:
            return data, "The signatures don't match"

        return data, None

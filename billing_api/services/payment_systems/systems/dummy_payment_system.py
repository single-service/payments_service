import uuid
from typing import Any, Dict, Optional, Tuple

from django.contrib.auth import get_user_model

from billing.payment_systems.main_interface import PaymentSystemInterface


User = get_user_model()


class PaymentSystemService(PaymentSystemInterface):
    host = "core.ai.conlami.com"

    @classmethod
    def create_link(cls, payment_data: Dict[str, Any], purchaser: User) -> str:
        """Creates link for the given user's payment"""
        user_id = purchaser.id
        value = payment_data["sum"]
        currency_name = payment_data["currency_name"]
        return cls._generate_link(user_id, value, currency_name)

    @classmethod
    def check_payment(cls, payment_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Checks the payment"""
        result = {
            "user_id": payment_data["user_id"],
            "sum": payment_data["sum"],
            "currency": payment_data["currency"],
        }
        return result, None

    @classmethod
    def _generate_link(cls, user_id: uuid.UUID, value: float, currency_name: str) -> str:
        return "https://%(host)s/billing/dummy-payment?user_id=%(user_id)s&sum=%(sum)s&currency=%(currency)s" % {
            "host": cls.host,
            "user_id": user_id,
            "sum": value,
            "currency": currency_name,
        }

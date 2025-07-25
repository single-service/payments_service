import uuid
from typing import Any, Dict, Optional, Tuple

from app.services.payment_systems.main_interface import PaymentSystemInterface


class DummyPaymentSystemService(PaymentSystemInterface):

    def __init__(self):
        self.HOST = None

    def create_link(self, final_amount, user_email, description, payment_id, operation_id=0, is_subscription=False, nomenclature=None) -> str:
        """Creates link for the given user's payment"""
        user_id = user_email
        value = final_amount
        currency_name = payment_id
        return self._generate_link(user_id, value, currency_name)

    @classmethod
    def check_payment(cls, payment_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Checks the payment"""
        result = {
            "user_id": payment_data["user_id"],
            "sum": payment_data["sum"],
            "currency": payment_data["currency"],
        }
        return result, None


    def _generate_link(self, user_id: uuid.UUID, value: float, currency_name: str) -> str:
        return "https://%(host)s/billing/dummy-payment?user_id=%(user_id)s&sum=%(sum)s&currency=%(currency)s" % {
            "host": self.HOST,
            "user_id": user_id,
            "sum": value,
            "currency": currency_name,
        }

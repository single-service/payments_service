from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from django.contrib.auth import get_user_model
from rest_framework.request import Request

from billing.models import UserPayment


User = get_user_model()


class PaymentSystemInterface(ABC):
    host: str = None

    @abstractmethod
    def create_link(self, payment_data: Dict[str, Any], purchaser: User, user_payment: UserPayment):
        """Creates payment link"""
        raise NotImplementedError()

    @abstractmethod
    def check_payment(self, request: Request) -> Tuple[Optional[dict], Optional[str]]:
        """Checks the success of the payment"""
        raise NotImplementedError()

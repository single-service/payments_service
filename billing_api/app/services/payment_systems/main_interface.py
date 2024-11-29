from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
from decimal import Decimal

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_connector import get_async_session


class PaymentSystemInterface(ABC):

    @abstractmethod
    def create_link(self, final_amount: Decimal, user_email: str, description: Optional[str], order_id: str, invoice_id: str, is_subscription=False):
        """Creates payment link"""
        raise NotImplementedError()

    @abstractmethod
    def check_payment(self, request) -> Tuple[Optional[dict], Optional[str]]:
        """Checks the success of the payment"""
        raise NotImplementedError()

    def set_system_parameters(self, *args, **kwargs):
        for param_name, param_value in kwargs.items():
            setattr(self, param_name, param_value)

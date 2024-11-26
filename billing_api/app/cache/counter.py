import logging
import uuid

from fastapi import Depends, HTTPException

from .cacher import Cacher
from app.services.users import UserService
from app.enums import TariffLimitNameChoice


logger = logging.getLogger("info")


class APICountManager:
    """Считает запросы каждого пользователя к API. Следит за балансом."""

    def __init__(
        self,
        cacher: Cacher = Depends(Cacher),
        user_service: UserService = Depends(UserService),
    ):
        self.cacher = cacher
        self.user_service = user_service

    # old billing
    # async def check_balance(self, user_id: str):
    #     """Проверяет баланс пользователя"""

    #     balance = await self.user_service.get_user_balance(user_id)
    #     user = await self.user_service.get_user(user_id)
    #     if not user.billing_currency:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Select the currency in the settings.",
    #         )
    #     if balance is None:
    #         logger.error(f"Balance was not retrieved. user_id : '{user_id}'.")
    #         raise HTTPException(
    #             status_code=400,
    #             detail=f"Invalid 'user_id' was passed: {user_id}.",
    #         )

    #     if balance <= 0:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Low balance.",
    #         )

    # async def balance_manage(self, user_id: str, is_owner: bool):
    #     """Определяет чья модель и уменьшает баланс"""

    #     await self.check_balance(user_id)                                    # Проверяем баланс
    #     expense_name = 'model_prediction' if is_owner else 'ai_model_rental'
    #     await self.user_service.dcr_user_balance(user_id, expense_name)      # Уменьшаем баланс

    async def check_user_tariff_limit(self, user_id: uuid, is_owner: bool) -> None:
        """
        Проверяет есть ли лимиты у пользователя

        :param user_id: Значение id пользователя для которого нужно обновить лимит.
        :param is_owner: Флаг, указывающий, является ли пользователь владельцем модели.
        """
        user = await self.user_service.get_user(user_id)
        tariff_limit_choice = TariffLimitNameChoice.OWN_MODEL_PREDICTION_COUNT.value if is_owner \
            else TariffLimitNameChoice.RENTED_MODEL_PREDICTION_COUNT.value

        success, message = await self.user_service.check_user_tariff_limit(user.id, tariff_limit_choice)
        if not success:
            logger.error(message)
            raise HTTPException(status_code=400, detail=message)

    async def add_user_tariff_limit(self, user_id: uuid, is_owner: bool):
        """
        Функция для добавления значения к current_value в UserTariffLimit
        в зависимости от TariffLimit.name и пользователя User.

        :param user_id: Значение id пользователя для которого нужно обновить лимит.
        :param is_owner: Флаг, указывающий, является ли пользователь владельцем модели.
        """
        user = await self.user_service.get_user(user_id)
        tariff_limit_choice = TariffLimitNameChoice.OWN_MODEL_PREDICTION_COUNT.value if is_owner \
            else TariffLimitNameChoice.RENTED_MODEL_PREDICTION_COUNT.value

        success, message = await self.user_service.add_user_tariff_limit(user.id, tariff_limit_choice)
        if not success:
            logger.error(message)
            raise HTTPException(status_code=400, detail=message)

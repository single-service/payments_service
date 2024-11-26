import uuid
import datetime

from typing import Any, List

from pydantic import BaseModel


class PredictionResponse(BaseModel):
    """Схема ответа сервера на запрос предикта"""

    predictions: List[Any]


class ModelPredictionsResponse(BaseModel):
    """Схема ответа на запрос всех предиктов модели"""

    id: uuid.UUID
    data: str
    prediction: str
    true_prediction: str
    created_dt: datetime.datetime
    updated_dt: datetime.datetime

    class Config:
        orm_mode = True

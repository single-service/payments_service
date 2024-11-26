from typing import List, Any, Union, Dict, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, conlist, constr, Field


PredictRequestBody = Union[
    conlist(
        conlist(Any, min_items=1),
        min_items=1,
    ),
    str,
]


class PredictionResponse(BaseModel):
    """Схема ответа сервера на запрос предикта"""

    predictions: List[Any]


class ModelPredictionsResponse(BaseModel):
    """Схема ответа на запрос всех предиктов модели"""

    id: UUID
    data: str
    prediction: str
    true_prediction: str
    created_dt: datetime
    updated_dt: datetime

    class Config:
        orm_mode = True


class PredictionUpdateRequest(BaseModel):
    """Схема данных запроса для обновления предикта"""

    true_prediction: constr(max_length=150, min_length=1)


class CallbackConfig(BaseModel):
    url: str = Field(..., description="Ссылка для коллбэка после предсказания")
    headers: Optional[Dict[str, Any]] = Field(None, description="Заголовки callback-запроса")
    timeout: Optional[int] = Field(60, description="Ограничение на таймаут запроса")


class PredictWithCallbackRequestBody(BaseModel):
    callback_config: CallbackConfig
    input_data: PredictRequestBody = Field(..., description="Входные данные для предсказания")

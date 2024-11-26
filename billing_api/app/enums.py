from enum import Enum


# class TariffLimitNameChoice(Enum):
#     # Количество моделей ИИ
#     AI_MODEL_COUNT = (1, 'Количество моделей ИИ')
#     # Количество версий моделей ИИ
#     AI_MODEL_VERSION_COUNT = (2, 'Количество версий моделей ИИ')
#     # Количество датасетов
#     DATASET_COUNT = (3, 'Количество датасетов')
#     # Количество предсказаний на собственных моделях
#     OWN_MODEL_PREDICTION_COUNT = (4, 'Количество предсказаний на собственных моделях')
#     # Количество предсказаний на арендованных моделях
#     RENTED_MODEL_PREDICTION_COUNT = (5, 'Количество предсказаний на арендованных моделях')
#     # Количество операций сборщика данных
#     DATA_COLLECTOR_OPERATION_COUNT = (6, 'Количество операций сборщика данных')
#     # Количество операций по подготовке датасета
#     DATASET_PREPARATION_OPERATION_COUNT = (7, 'Количество операций по подготовке датасета')

#     def __new__(cls, value, label):
#         obj = object.__new__(cls)
#         obj._value_ = value
#         obj.label = label
#         return obj

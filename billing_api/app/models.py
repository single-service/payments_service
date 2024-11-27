from app.database_connector import AutoBase
from sqlalchemy.orm import relationship

# SQLAlchemy создает связи по названию таблиц! т.е. AIUserModelVersion имеет FK на AIUserModel, \
#  поэтому вместо user_model_version.user_model будет так: user_model_version.aimodels_aiusermodel


Application = AutoBase.classes.applications_application
ApplicationToken = AutoBase.classes.applications_applicationtoken
PaymentSystemParamter = AutoBase.classes.applications_paymentsystemparamter

PaymentItemsGroup = AutoBase.classes.payments_paymentitemsgroup
PaymentItem = AutoBase.classes.payments_paymentitem
PaymentItemDiscount = AutoBase.classes.payments_paymentitemdiscount

Order = AutoBase.classes.billing_order

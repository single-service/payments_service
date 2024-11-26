from app.database_connector import AutoBase

# SQLAlchemy создает связи по названию таблиц! т.е. AIUserModelVersion имеет FK на AIUserModel, \
#  поэтому вместо user_model_version.user_model будет так: user_model_version.aimodels_aiusermodel


User = AutoBase.classes.users_user
UserToken = AutoBase.classes.users_usertoken
Country = AutoBase.classes.users_country
CountryRegion = AutoBase.classes.users_countryregion

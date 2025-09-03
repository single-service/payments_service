#  Сервис платежей
repo gitverse - (https://gitverse.ru/disosedov/payment-service)
repo github - (https://github.com/single-service/payments_service.git)
dockerhub - (https://hub.docker.com/repository/docker/singleservice/ru_billing_service/general)

### Компоненты
db - PostgresBD
web - админка и миграции на Django
api - api на FastApi
redis - для кэша

### Запуск приложения
```sh
docker compose up -d --build
```

Необходимо создать суперадмина

```sh
docker compose exec admin python manage.py createsuper
```

Админка - http://0.0.0.0:8008
API - http://0.0.0.0:8007/api/v1/docs

В админке основные модели:
Приложения - это наименование нашего приложения, вводим название, вид платежной системы и параметры, также callback_url
В этом е интерфейсе через action Создать токен - создаем токен для приложения , копируем его себе тобы не потерять.

Создаем группы платежных позиций - это просто наименование группы товаров
Создаем платежные позиции.

Для локальной разработки понадобится сервисы типа ngrok, tuna.
tuna http 8008 --subdomain=payment-esu


# Урл успешный
https://xn----ctbefqt5agebvc.xn--p1ai/?OutSum=500.00&InvId=6&Shp_operation_id=5719897e-126b-4a51-b9a7-fb037c515ae0&Shp_user_payment_id=294ff5c0-de82-4a77-800a-6c72af4dcba0&SignatureValue=28db82b7f59030b6676fa1a4abb1e905&IsTest=1&Culture=ru
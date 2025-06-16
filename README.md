#  Сервис платежей
repo - (https://gitverse.ru/disosedov/payment-service)
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


### TODO
- [X] Перенести апи в контейнер
- [ ] Колбэкурл
- [ ] Фискализация
- [X] Скрипт публикации в DockerHub
- [ ] В ответе по созданию заказа если он уже есть возвращать снова тело заказа

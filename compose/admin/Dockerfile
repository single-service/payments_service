# Базовый образ
FROM python:3.12

# Отключаем буферизацию и записывание байт-кода
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Устанавливаем зависимости для Python и системы, включая PostgreSQL 17
RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  && apt-get install -y supervisor \
  && apt-get install -y nginx \
  && apt-get install -y gettext \
  # cleaning up unused files
  && apt-get install -y curl \
  && apt-get install -y netcat-traditional \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
ENV HOME=/billing_manager/
WORKDIR $HOME

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем и настраиваем скрипт запуска
COPY ./compose/admin/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start
COPY ./compose/admin/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint
COPY ./compose/admin/api_start /api_start
RUN sed -i 's/\r$//g' /api_start && chmod +x /api_start

# Копируем конфигурацию nginx
RUN rm /etc/nginx/nginx.conf
COPY compose/admin/nginx.conf /etc/nginx/nginx.conf
COPY compose/admin/default.conf /etc/nginx/conf.d/default.conf

# Копируем конфигурацию для supervisord
COPY compose/admin/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Копируем все файлы приложения
COPY ./billing_admin .

COPY ./billing_api ./billing_api

ENTRYPOINT [ "/entrypoint" ]
# Запуск supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
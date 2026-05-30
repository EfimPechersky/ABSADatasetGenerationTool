FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    unzip \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка huggingface-hub для скачивания моделей
RUN pip install --no-cache-dir huggingface-hub

# Копирование кастомной библиотеки
COPY custom_libs/pyabsa /usr/local/lib/python3.12/site-packages/pyabsa

COPY Backend/ ./Backend/

ENV LLM_API_URL=""
ENV SECRET_KEY="your-super-secret-key-change-this-to-something-very-secure-2026"
ENV ALGORITHM="HS256"
ENV ACCESS_TOKEN_EXPIRE_MINUTES="60"

# Отключаем проверку CUDA и git
ENV CUDA_VISIBLE_DEVICES=""
ENV GIT_PYTHON_REFRESH="quiet"

EXPOSE 8000

# Скрипт для ожидания БД и инициализации
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Запуск с ожиданием БД
CMD ["/wait-for-it.sh", "postgres","5432", "--", "uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
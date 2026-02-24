FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Увеличен таймаут для медленного интернета (Django, pandas — большие пакеты)
RUN pip install --no-cache-dir --timeout 300 -r requirements.txt
# Явная установка rapidfuzz (иногда не ставится из -r на части окружений)
RUN pip install --no-cache-dir --timeout 120 rapidfuzz>=3.0.0

COPY . .

EXPOSE 8000

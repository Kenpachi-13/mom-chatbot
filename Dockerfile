# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on \
    TZ=Europe/Berlin

# Системные зависимости (минимум)
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала зависимости — для кеша
COPY requirements.txt .
# Чуть фиксируем pip, чтобы не было сюрпризов
RUN python -m pip install --upgrade pip==24.2 && \
    pip install -r requirements.txt

# Затем код
COPY . .

# Безопасность (не root)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Запуск
CMD ["python", "bot.py"]

# Используем стабильный Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Переменные окружения (чтобы логи сразу печатались)
ENV PYTHONUNBUFFERED=1

# Команда запуска бота
CMD ["python", "bot.py"]

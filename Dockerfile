FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаём папку для загрузок (если нужно)
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Запускаем твой бот напрямую
CMD ["python", "main.py"]

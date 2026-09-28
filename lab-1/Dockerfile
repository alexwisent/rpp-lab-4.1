# Стадия 1: сборка зависимостей
FROM python:3.11-slim AS builder

WORKDIR /app

# Создаём виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Сначала копируем только requirements.txt и ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Стадия 2: финальный образ
FROM python:3.11-slim

WORKDIR /app

# Копируем готовое виртуальное окружение из стадии сборки
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем код приложения
COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
import os
from datetime import datetime, timezone
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 1. Загружаем переменные из .env в окружение процесса
load_dotenv()

app = Flask(__name__)

# 2. Читаем переменные окружения
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")
DB_NAME = os.getenv("DB_NAME", "visits")

# 3. Кодируем пароль на случай спецсимволов (@, :, / и т.п.)
password = quote_plus(DB_PASSWORD)

# 4. Собираем строку подключения
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 5. Инициализируем SQLAlchemy
db = SQLAlchemy(app)


# Модель Visit
class Visit(db.Model):
    __tablename__ = "visits"

    id = db.Column(db.Integer, primary_key=True)
    visited_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    ip_address = db.Column(db.String(45), nullable=False)

@app.get("/")
def index():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
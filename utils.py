import json
import time
from datetime import datetime, timedelta
import requests
import uvicorn

from sqlalchemy import Integer, String, Float, DateTime, Column
from sqlalchemy.orm import Session

from config import Base, SessionLocal, HOST_IP


class Currency(Base):
    """
    Модель валюты в БД
    """
    __tablename__ = 'currencies'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    rate = Column(Float)
    timestamp = Column(DateTime)


def schedule_currency_rate_update():
    db = SessionLocal()
    load_currency_rate(db)
    db.close()


def load_currency_rate(db: Session):
    # Здесь код для получения курса валюты с помощью API
    # API от Центрального Банка России
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    data = json.loads(response.text)

    currency_rate = data["Valute"]["USD"]["Value"]
    print(currency_rate)

    new_currency = Currency(name="USD", rate=currency_rate, timestamp=datetime.now())

    # Добавление нового курса валюты в базу данных
    db.add(new_currency)
    db.commit()
    db.refresh(new_currency)


def get_db():
    """
    Функция для получения сессии базы данных
    return: SessionLocal
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_scheduler():
    while True:
        # Загрузка курса валюты и сохранение его в базу данных
        db = SessionLocal()
        load_currency_rate(db)
        db.close()

        # Ожидание до следующего дня
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        time.sleep((tomorrow - datetime.now()).total_seconds())


def main_loop():
    uvicorn.run("main:app", host=HOST_IP, port=3401)

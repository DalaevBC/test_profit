import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from utils import schedule_currency_rate_update, Currency, get_db, set_scheduler, main_loop


app = FastAPI()


@app.get('/currency')
def get_currency(db: Session = Depends(get_db)):
    currency = db.query(Currency).order_by(Currency.timestamp.desc()).first()
    return {'currency': currency.name, 'rate': currency.rate}


@app.get('/currency/history')
def get_currency_history(db: Session = Depends(get_db)):
    history = db.query(Currency).order_by(Currency.timestamp.desc()).all()
    return {
        'history': [
            {'currency': c.name,
             'rate': c.rate,
             'timestamp': c.timestamp} for c in history
        ]
    }


scheduler = BackgroundScheduler()
scheduler.add_job(schedule_currency_rate_update, IntervalTrigger(days=1))
scheduler.start()


if __name__ == '__main__':
    # Создание двух потоков
    scheduler_thread = threading.Thread(target=set_scheduler)
    main_thread = threading.Thread(target=main_loop)

    # Запуск потоков
    scheduler_thread.start()
    main_thread.start()

    # Ожидание завершения потоков
    scheduler_thread.join()
    main_thread.join()


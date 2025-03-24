from celery import shared_task
from datetime import datetime

@shared_task
def periodic_heartbeat():
    print("🔁 Heartbeat:", datetime.now())
    return {"status": "ok", "time": str(datetime.now())}

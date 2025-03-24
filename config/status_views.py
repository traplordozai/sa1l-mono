from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_celery_results.models import TaskResult
import redis
from django.conf import settings

@api_view(["GET"])
def system_status(request):
    redis_ok = False
    try:
        r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        redis_ok = True
    except:
        pass

    latest = TaskResult.objects.order_by("-date_done").first()

    return Response({
        "celery": "OK" if latest else "No recent task",
        "redis": "OK" if redis_ok else "DOWN",
        "last_task": latest.task_name if latest else "N/A",
        "last_runtime": latest.date_done.isoformat() if latest else "N/A"
    })

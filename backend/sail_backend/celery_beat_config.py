from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'heartbeat-every-1-minute': {
        'task': 'config.tasks.periodic_heartbeat',
        'schedule': crontab(minute='*/1'),
    },
}

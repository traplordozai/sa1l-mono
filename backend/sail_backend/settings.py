INSTALLED_APPS += ["rest_framework", "rest_framework_simplejwt",
                   "rest_framework_simplejwt.token_blacklist",
                   "forms"
]

AUTH_USER_MODEL = 'users.User'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Dev only

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

ASGI_APPLICATION = 'sail_backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [("localhost", 6379)],
        },
    },
}

MIDDLEWARE += ['users.middleware.UserActivityLoggerMiddleware']

LOGGING = {
    "version": 1,
    "handlers": {
        "console": { "class": "logging.StreamHandler" },
    },
    "loggers": {
        "applications": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# DeepSeek AI API Configuration
DEEPSEEK_API_KEY = 'your-api-key-here'  # Remember to use environment variables in production


CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

import os
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

CELERY_IMPORTS = ['config.tasks']

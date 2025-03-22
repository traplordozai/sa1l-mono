"""
Development settings - extends the base settings
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# SECURITY WARNING: Use a different key in production!
SECRET_KEY = "django-insecure-dev-environment-change-this-in-production"

# Additional development apps
INSTALLED_APPS += [

]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Debug toolbar settings
INTERNAL_IPS = [
    "127.0.0.1",
]

# Email backend for development - prints to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable security features that would break local development
CORS_ALLOW_ALL_ORIGINS = True
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Simplified JWT settings for development
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(days=1)

# Make logs directory if it doesn't exist
import os

os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

# Set more verbose logging for development
LOGGING["loggers"]["django"]["level"] = "DEBUG"
LOGGING["loggers"]["backend"]["level"] = "DEBUG"

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sail_backend.settings")

try:
    application = get_wsgi_application()
except Exception as e:
    import sys
    print("WSGI application failed to start:", e, file=sys.stderr)
    raise
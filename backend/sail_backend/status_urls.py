from django.urls import path
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from redis import Redis

def health_check(request):
    """Health check endpoint that verifies database and cache connectivity"""
    status = {
        "status": "healthy",
        "database": "healthy",
        "cache": "healthy",
        "version": "1.0.0"
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        status["database"] = "unhealthy"
        status["database_error"] = str(e)
        status["status"] = "unhealthy"
    
    # Check cache
    try:
        cache.set("health_check", "ok", timeout=10)
        if cache.get("health_check") != "ok":
            raise Exception("Cache get/set failed")
    except Exception as e:
        status["cache"] = "unhealthy"
        status["cache_error"] = str(e)
        status["status"] = "unhealthy"
    
    return JsonResponse(status)

urlpatterns = [
    path("health/", health_check, name="health-check"),
] 
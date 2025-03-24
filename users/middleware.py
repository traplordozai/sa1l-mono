from activity.models import ActivityLog

class LogActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.path.startswith("/api/v1/"):
            ActivityLog.objects.create(
                actor=request.user,
                action=request.method,
                target=request.path,
                meta={"status": response.status_code}
            )
        return response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from ..activity.models import ActivityLog

@api_view(["GET"])
@permission_classes([IsAdminUser])
def activity_feed(request):
    logs = ActivityLog.objects.select_related("actor").order_by("-timestamp")[:100]
    return Response([
        {
            "id": log.id,
            "user": log.actor.username if log.actor else "Anonymous",
            "action": log.action,
            "target": log.target,
            "meta": log.meta,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ])

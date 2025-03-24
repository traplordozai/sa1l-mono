from django.core.management.base import BaseCommand
from internships.models.document import Document
from django.utils import timezone

class Command(BaseCommand):
    help = "Auto-flag expired documents"

    def handle(self, *args, **options):
        now = timezone.now()
        expired = Document.objects.filter(expires_at__lt=now, status__in=["draft", "submitted"])
        for doc in expired:
            doc.status = "expired"
            doc.save()
        self.stdout.write(f"{expired.count()} documents marked as expired.")
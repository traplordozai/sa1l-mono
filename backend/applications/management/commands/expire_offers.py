from django.core.management.base import BaseCommand
from applications.models import Application
from django.utils import timezone
from users.utils import notify_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Expire offers past their expiration window"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview without modifying data')
        parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        start = options.get('start')
        end = options.get('end')

        now = timezone.now()

        qs = Application.objects.filter(status="offered", expires_at__lt=now)

        if start:
            start_dt = timezone.make_aware(datetime.strptime(start, "%Y-%m-%d"))
            qs = qs.filter(expires_at__gte=start_dt)
        if end:
            end_dt = timezone.make_aware(datetime.strptime(end, "%Y-%m-%d"))
            qs = qs.filter(expires_at__lte=end_dt)

        expired_count = 0

        for app in qs.iterator():
            logger.info(f"Expiring offer ID={app.id} for candidate={app.candidate.username} (position={app.position})")
            if not dry_run:
                app.status = "stale"
                app.save(update_fields=["status"])

                notify_user(app.candidate.id, {
                    "title": "Offer Expired",
                    "message": f"Your offer for '{app.position}' has expired.",
                })

            expired_count += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY RUN] {expired_count} offers would be marked stale"))
        else:
            self.stdout.write(self.style.SUCCESS(f"{expired_count} offers marked as stale"))
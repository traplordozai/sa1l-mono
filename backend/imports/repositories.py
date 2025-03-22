from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction
from django.utils import timezone

from .models import ImportDetail, ImportLog, ImportStatus, ImportType


class ImportRepository:
    """
    Repository for managing import operations and logs
    """

    @classmethod
    def create_import_log(
        cls,
        import_type: str,
        file_name: str,
        file_size: int,
        original_file_name: str,
        imported_by=None,
    ) -> ImportLog:
        """
        Create a new import log entry
        """
        return ImportLog.objects.create(
            import_type=import_type,
            file_name=file_name,
            file_size=file_size,
            original_file_name=original_file_name,
            imported_by=imported_by,
            status=ImportStatus.PENDING,
        )

    @classmethod
    def update_import_started(cls, import_log_id: str) -> ImportLog:
        """
        Mark an import as started
        """
        import_log = ImportLog.objects.get(id=import_log_id)
        import_log.status = ImportStatus.PROCESSING
        import_log.started_at = timezone.now()
        import_log.save(update_fields=["status", "started_at", "updated_at"])
        return import_log

    @classmethod
    def update_import_completed(
        cls,
        import_log_id: str,
        success_count: int,
        error_count: int,
        warnings_count: int,
        processed_count: int,
        errors: Dict = None,
        warnings: Dict = None,
    ) -> ImportLog:
        """
        Mark an import as completed with results
        """
        import_log = ImportLog.objects.get(id=import_log_id)
        now = timezone.now()

        # Calculate execution time
        if import_log.started_at:
            execution_seconds = int((now - import_log.started_at).total_seconds())
        else:
            execution_seconds = None

        # Determine status based on results
        if error_count == 0 and warnings_count == 0:
            status = ImportStatus.COMPLETED
        elif error_count > 0 and success_count == 0:
            status = ImportStatus.FAILED
        else:
            status = ImportStatus.PARTIALLY_COMPLETED

        # Update the import log
        import_log.status = status
        import_log.success_count = success_count
        import_log.error_count = error_count
        import_log.warnings_count = warnings_count
        import_log.processed_count = processed_count
        import_log.completed_at = now
        import_log.execution_time = execution_seconds

        if errors:
            import_log.errors = errors
        if warnings:
            import_log.warnings = warnings

        import_log.save()
        return import_log

    @classmethod
    def update_import_failed(cls, import_log_id: str, error: str) -> ImportLog:
        """
        Mark an import as failed with error message
        """
        import_log = ImportLog.objects.get(id=import_log_id)
        now = timezone.now()

        # Calculate execution time if possible
        if import_log.started_at:
            execution_seconds = int((now - import_log.started_at).total_seconds())
        else:
            execution_seconds = None

        import_log.status = ImportStatus.FAILED
        import_log.errors = {"general_error": error}
        import_log.completed_at = now
        import_log.execution_time = execution_seconds
        import_log.save()
        return import_log

    @classmethod
    def add_import_detail(
        cls,
        import_log_id: str,
        entity_type: str,
        row_number: Optional[int],
        original_data: Dict,
        processed_data: Optional[Dict],
        status: str,
        message: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> ImportDetail:
        """
        Add a detail record for an imported entity
        """
        import_log = ImportLog.objects.get(id=import_log_id)

        return ImportDetail.objects.create(
            import_log=import_log,
            entity_type=entity_type,
            entity_id=entity_id,
            row_number=row_number,
            original_data=original_data,
            processed_data=processed_data,
            status=status,
            message=message,
        )

    @classmethod
    def update_task_id(cls, import_log_id: str, task_id: str) -> ImportLog:
        """
        Update the Celery task ID for an import
        """
        import_log = ImportLog.objects.get(id=import_log_id)
        import_log.task_id = task_id
        import_log.save(update_fields=["task_id", "updated_at"])
        return import_log

    @classmethod
    def get_import_log(cls, import_log_id: str) -> ImportLog:
        """
        Get an import log by ID
        """
        return ImportLog.objects.get(id=import_log_id)

    @classmethod
    def get_import_details(
        cls, import_log_id: str, status: Optional[str] = None
    ) -> List[ImportDetail]:
        """
        Get import details for a specific import log
        """
        query = ImportDetail.objects.filter(import_log_id=import_log_id)
        if status:
            query = query.filter(status=status)
        return list(query)

    @classmethod
    def get_recent_imports(cls, limit: int = 10) -> List[ImportLog]:
        """
        Get recent imports
        """
        return list(ImportLog.objects.all().order_by("-created_at")[:limit])

import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone

from .models import ImportStatus, ImportType
from .repositories import ImportRepository


class BaseImportService:
    """
    Base service for file imports with common functionality
    """

    def __init__(self, user=None):
        self.user = user
        self.upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_uploaded_file(self, file) -> Tuple[str, str, int]:
        """
        Save an uploaded file to a temporary location and return its path

        Returns:
            Tuple containing:
                - File path
                - Generated file name
                - File size in bytes
        """
        unique_name = f"{uuid.uuid4()}_{file.name}"
        file_path = os.path.join(self.upload_dir, unique_name)

        # Save the file
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return file_path, unique_name, file.size

    def create_import_log(
        self, import_type: str, file_name: str, file_size: int, original_file_name: str
    ) -> str:
        """
        Create an import log entry

        Returns:
            ID of the created import log
        """
        import_log = ImportRepository.create_import_log(
            import_type=import_type,
            file_name=file_name,
            file_size=file_size,
            original_file_name=original_file_name,
            imported_by=self.user,
        )
        return str(import_log.id)

    def update_task_id(self, import_log_id: str, task_id: str):
        """
        Update the Celery task ID for an import
        """
        ImportRepository.update_task_id(import_log_id, task_id)

    def cleanup_file(self, file_path: str):
        """
        Remove a temporary file
        """
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Log but don't fail if cleanup fails
                print(f"Warning: Failed to remove temporary file {file_path}: {str(e)}")

    def get_import_status(self, import_log_id: str) -> Dict:
        """
        Get the status of an import
        """
        import_log = ImportRepository.get_import_log(import_log_id)
        return {
            "id": str(import_log.id),
            "status": import_log.status,
            "file_name": import_log.original_file_name,
            "import_type": import_log.import_type,
            "processed_count": import_log.processed_count,
            "success_count": import_log.success_count,
            "error_count": import_log.error_count,
            "warnings_count": import_log.warnings_count,
            "started_at": (
                import_log.started_at.isoformat() if import_log.started_at else None
            ),
            "completed_at": (
                import_log.completed_at.isoformat() if import_log.completed_at else None
            ),
            "execution_time": import_log.execution_time,
            "created_at": import_log.created_at.isoformat(),
            "updated_at": import_log.updated_at.isoformat(),
            "success_rate": import_log.success_rate,
        }


class StudentCsvImportService(BaseImportService):
    """
    Service for importing student data from CSV files
    """

    def prepare_import(self, file) -> Dict:
        """
        Prepare a student CSV import

        Returns:
            Dict with import details including import_log_id and file_path
        """
        # Save the uploaded file
        file_path, file_name, file_size = self.save_uploaded_file(file)

        # Create import log
        import_log_id = self.create_import_log(
            import_type=ImportType.STUDENT_CSV,
            file_name=file_name,
            file_size=file_size,
            original_file_name=file.name,
        )

        return {
            "import_log_id": import_log_id,
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_size,
        }


class OrganizationCsvImportService(BaseImportService):
    """
    Service for importing organization data from CSV files
    """

    def prepare_import(self, file) -> Dict:
        """
        Prepare an organization CSV import

        Returns:
            Dict with import details including import_log_id and file_path
        """
        # Save the uploaded file
        file_path, file_name, file_size = self.save_uploaded_file(file)

        # Create import log
        import_log_id = self.create_import_log(
            import_type=ImportType.ORGANIZATION_CSV,
            file_name=file_name,
            file_size=file_size,
            original_file_name=file.name,
        )

        return {
            "import_log_id": import_log_id,
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_size,
        }


class GradesPdfImportService(BaseImportService):
    """
    Service for importing student grades from PDF files
    """

    def prepare_import(self, file, student_id=None) -> Dict:
        """
        Prepare a grades PDF import

        Args:
            file: The uploaded PDF file
            student_id: Optional student ID to associate with the grades

        Returns:
            Dict with import details including import_log_id and file_path
        """
        # Save the uploaded file
        file_path, file_name, file_size = self.save_uploaded_file(file)

        # Create import log
        import_log_id = self.create_import_log(
            import_type=ImportType.GRADES_PDF,
            file_name=file_name,
            file_size=file_size,
            original_file_name=file.name,
        )

        return {
            "import_log_id": import_log_id,
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_size,
            "student_id": student_id,
        }


class StatementCsvImportService(BaseImportService):
    """
    Service for importing student statements from CSV files
    """

    def prepare_import(self, file) -> Dict:
        """
        Prepare a statement CSV import

        Returns:
            Dict with import details including import_log_id and file_path
        """
        # Save the uploaded file
        file_path, file_name, file_size = self.save_uploaded_file(file)

        # Create import log
        import_log_id = self.create_import_log(
            import_type=ImportType.STATEMENT_CSV,
            file_name=file_name,
            file_size=file_size,
            original_file_name=file.name,
        )

        return {
            "import_log_id": import_log_id,
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_size,
        }

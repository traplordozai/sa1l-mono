import logging
import os

from celery import shared_task
from django.db import transaction

from .processors.grades_pdf import GradesPdfProcessor
from .processors.student_csv import StudentCsvProcessor
from .repositories import ImportRepository
from .services import (GradesPdfImportService, OrganizationCsvImportService,
                       StatementCsvImportService, StudentCsvImportService)

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_student_csv_task(self, file_path, import_log_id):
    """
    Process a student CSV file in the background
    """
    logger.info(f"Starting student CSV import task for {file_path}")

    try:
        processor = StudentCsvProcessor(import_log_id, file_path)
        result = processor.process()

        # Update task ID in import log
        ImportRepository.update_task_id(import_log_id, self.request.id)

        # Clean up file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {str(e)}")

        return result

    except Exception as e:
        logger.exception(f"Error in student CSV import task: {str(e)}")

        # Update import log with error
        ImportRepository.update_import_failed(import_log_id, str(e))

        # Clean up file even on error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        # Reraise for Celery
        raise


@shared_task(bind=True)
def process_grades_pdf_task(self, file_path, import_log_id, student_id=None):
    """
    Process a grades PDF file in the background
    """
    logger.info(f"Starting grades PDF import task for {file_path}")

    try:
        processor = GradesPdfProcessor(import_log_id, file_path, student_id)
        result = processor.process()

        # Update task ID in import log
        ImportRepository.update_task_id(import_log_id, self.request.id)

        # Clean up file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {str(e)}")

        return result

    except Exception as e:
        logger.exception(f"Error in grades PDF import task: {str(e)}")

        # Update import log with error
        ImportRepository.update_import_failed(import_log_id, str(e))

        # Clean up file even on error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        # Reraise for Celery
        raise


@shared_task(bind=True)
def process_organization_csv_task(self, file_path, import_log_id):
    """
    Process an organization CSV file in the background
    """
    logger.info(f"Starting organization CSV import task for {file_path}")

    try:
        # This would use OrganizationCsvProcessor in a real implementation
        # Just a placeholder for now
        result = {
            "import_log_id": import_log_id,
            "processed_count": 0,
            "success_count": 0,
            "error_count": 0,
            "warning_count": 0,
        }

        # Update task ID in import log
        ImportRepository.update_task_id(import_log_id, self.request.id)

        # Update import log with failure since this is just a placeholder
        ImportRepository.update_import_failed(
            import_log_id, "Organization CSV import not implemented yet"
        )

        # Clean up file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        return result

    except Exception as e:
        logger.exception(f"Error in organization CSV import task: {str(e)}")

        # Update import log with error
        ImportRepository.update_import_failed(import_log_id, str(e))

        # Clean up file even on error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        # Reraise for Celery
        raise

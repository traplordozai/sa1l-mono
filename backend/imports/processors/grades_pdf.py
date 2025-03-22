import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import pdfplumber
from backend.grades.repositories import GradeRepository
from django.db import transaction
from django.utils import timezone

from backend.students.models import Student
from backend.students.repositories import StudentRepository

from ..repositories import ImportRepository

logger = logging.getLogger(__name__)


class GradesPdfProcessor:
    """
    Processor for student grades PDF imports
    """

    def __init__(
        self, import_log_id: str, file_path: str, student_id: Optional[str] = None
    ):
        self.import_log_id = import_log_id
        self.file_path = file_path
        self.student_id = student_id
        self.success_count = 0
        self.error_count = 0
        self.warning_count = 0
        self.processed_count = 0
        self.errors = {}
        self.warnings = {}

    def process(self) -> Dict:
        """
        Process the PDF file

        Returns:
            Dict with processing results
        """
        try:
            # Mark import as started
            ImportRepository.update_import_started(self.import_log_id)

            # Extract text from PDF
            pdf_text = self._extract_text_from_pdf()
            if not pdf_text:
                ImportRepository.update_import_failed(
                    self.import_log_id, "PDF file is empty or could not be read"
                )
                return self._get_result_dict()

            # Parse student info if student_id was not provided
            student = None
            if self.student_id:
                # Try to get student by ID
                try:
                    student = StudentRepository.get_student_by_student_id(
                        self.student_id
                    )
                except Student.DoesNotExist:
                    error_msg = f"No student found with ID: {self.student_id}"
                    ImportRepository.update_import_failed(self.import_log_id, error_msg)
                    self._add_error(None, error_msg)
                    return self._get_result_dict()
            else:
                # Try to extract student info from PDF
                student_info = self._parse_student_info(pdf_text)
                if not student_info or not student_info.get("student_id"):
                    error_msg = "Could not identify student from PDF"
                    ImportRepository.update_import_failed(self.import_log_id, error_msg)
                    self._add_error(None, error_msg)
                    return self._get_result_dict()

                # Try to get student by extracted ID
                try:
                    student = StudentRepository.get_student_by_student_id(
                        student_info["student_id"]
                    )
                except Student.DoesNotExist:
                    error_msg = (
                        f"No student found with ID: {student_info['student_id']}"
                    )
                    ImportRepository.update_import_failed(self.import_log_id, error_msg)
                    self._add_error(None, error_msg)
                    return self._get_result_dict()

            # Parse grades
            grades_data = self._parse_grades(pdf_text)
            if not grades_data:
                error_msg = f"No grades found in PDF for student {student.student_id}"
                ImportRepository.update_import_failed(self.import_log_id, error_msg)
                self._add_error(None, error_msg)
                return self._get_result_dict()

            # Process student grades
            self._process_grades(student, grades_data, pdf_text)

            # Mark import as completed
            ImportRepository.update_import_completed(
                self.import_log_id,
                success_count=self.success_count,
                error_count=self.error_count,
                warnings_count=self.warning_count,
                processed_count=self.processed_count,
                errors=self.errors,
                warnings=self.warnings,
            )

            return self._get_result_dict()

        except Exception as e:
            logger.exception(f"Error processing grades PDF: {str(e)}")
            ImportRepository.update_import_failed(self.import_log_id, str(e))
            return self._get_result_dict()

    def _extract_text_from_pdf(self) -> str:
        """
        Extract all text from a PDF file
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            self._add_error(None, f"Failed to extract text from PDF: {str(e)}")
            return ""

    def _parse_student_info(self, text: str) -> Optional[Dict[str, str]]:
        """
        Extract student identifying information from PDF text
        """
        # Match common patterns for student ID
        id_match = re.search(r"(?:Student|ID)[\s#:]+([A-Z0-9]+)", text, re.IGNORECASE)

        # Match patterns for student name
        name_match = re.search(
            r"(?:Name|Student)[\s:]+([A-Za-z\s,.-]+)", text, re.IGNORECASE
        )

        if not id_match and not name_match:
            self._add_error(None, "Could not find student ID or name in PDF")
            return None

        student_info = {}

        if id_match:
            student_info["student_id"] = id_match.group(1).strip()

        if name_match:
            full_name = name_match.group(1).strip()

            # Try to split into first and last name
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                student_info["first_name"] = name_parts[0]
                student_info["last_name"] = " ".join(name_parts[1:])
            else:
                student_info["full_name"] = full_name

        return student_info

    def _parse_grades(self, text: str) -> Dict[str, str]:
        """
        Extract course grades from PDF text
        """
        grades = {}

        # Define grade patterns for main courses
        course_patterns = {
            "constitutional_law": r"Constitutional Law[:\s]+([A-F][\+\-]?)",
            "contracts": r"Contracts[:\s]+([A-F][\+\-]?)",
            "criminal_law": r"Criminal Law[:\s]+([A-F][\+\-]?)",
            "property_law": r"Property[:\s]+([A-F][\+\-]?)",
            "torts": r"Torts[:\s]+([A-F][\+\-]?)",
        }

        # Extract main course grades
        for field, pattern in course_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                grades[field] = match.group(1)

        # Define LRW assignment patterns
        lrw_patterns = {
            "lrw_case_brief": r"Case Brief[:\s]+([A-F][\+\-]?)",
            "lrw_multiple_case": r"Multiple Case Analysis[:\s]+([A-F][\+\-]?)",
            "lrw_short_memo": r"Short Legal Memorandum[:\s]+([A-F][\+\-]?)",
        }

        # Extract LRW grades
        for field, pattern in lrw_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                grades[field] = match.group(1)

        return grades

    def _process_grades(self, student, grades_data: Dict[str, str], pdf_text: str):
        """
        Process and save student grades
        """
        self.processed_count += 1

        try:
            with transaction.atomic():
                # Create or update grade
                grade = GradeRepository.create_or_update_grade(
                    student_id=student.id,
                    grade_data=grades_data,
                    original_pdf_text=pdf_text,
                )

                # Log the successful import
                ImportRepository.add_import_detail(
                    import_log_id=self.import_log_id,
                    entity_type="grade",
                    row_number=None,
                    original_data={
                        "pdf_text": (
                            pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text
                        )
                    },
                    processed_data=grades_data,
                    status="success",
                    message=f"Successfully imported grades for student {student.first_name} {student.last_name}",
                    entity_id=str(grade.id),
                )

                self.success_count += 1

        except Exception as e:
            self._add_error(
                None,
                f"Error processing grades for student {student.student_id}: {str(e)}",
            )

            # Log the failed import
            ImportRepository.add_import_detail(
                import_log_id=self.import_log_id,
                entity_type="grade",
                row_number=None,
                original_data={
                    "pdf_text": (
                        pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text
                    )
                },
                processed_data=grades_data,
                status="error",
                message=str(e),
                entity_id=str(student.id),
            )

    def _add_error(self, row_index, message):
        """
        Add an error to the error collection
        """
        self.error_count += 1

        # Convert row_index to string for JSON serialization
        row_key = f"row_{row_index}" if row_index is not None else "general"

        if row_key not in self.errors:
            self.errors[row_key] = []

        self.errors[row_key].append(message)

    def _add_warning(self, row_index, message):
        """
        Add a warning to the warning collection
        """
        self.warning_count += 1

        # Convert row_index to string for JSON serialization
        row_key = f"row_{row_index}" if row_index is not None else "general"

        if row_key not in self.warnings:
            self.warnings[row_key] = []

        self.warnings[row_key].append(message)

    def _get_result_dict(self):
        """
        Get a dictionary with processing results
        """
        return {
            "import_log_id": self.import_log_id,
            "processed_count": self.processed_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "errors": self.errors,
            "warnings": self.warnings,
        }

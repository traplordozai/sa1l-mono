import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from core.events import (StatementGradedEvent, StudentCreatedEvent,
                         StudentMatchedEvent, StudentUpdatedEvent)
from core.handlers import EventBus
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from backend.core.cqrs import CommandDispatcher, QueryDispatcher
from backend.core.services import BaseService, DomainService

from .commands.student_commands import (CreateStudentCommand,
                                        DeleteStudentCommand,
                                        MatchStudentWithOrganizationCommand,
                                        UpdateStudentCommand)
from .models import (AreaOfLaw, SelfProposedExternship, Statement, Student,
                     StudentAreaRanking, StudentGrade, StudentProfile)
from .queries.get_student import (GetAllStudentsQuery, GetStudentByIdQuery,
                                  GetStudentProfileQuery, SearchStudentsQuery)
from .repositories import (AreaOfLawRepository,
                           SelfProposedExternshipRepository,
                           StatementRepository, StudentAreaRankingRepository,
                           StudentGradeRepository, StudentRepository)

logger = logging.getLogger(__name__)


class StudentService(BaseService):
    """Service for managing Student entities."""

    def __init__(self):
        # Repositories
        self.student_repo = StudentRepository()
        self.area_repo = AreaOfLawRepository()
        self.ranking_repo = StudentAreaRankingRepository()
        self.statement_repo = StatementRepository()
        self.grade_repo = StudentGradeRepository()
        self.externship_repo = SelfProposedExternshipRepository()
        self.event_bus = EventBus()
        self.student_repository = StudentRepository()

        # Set up command dispatcher
        self.command_dispatcher = CommandDispatcher()
        self.command_dispatcher.register(
            CreateStudentCommand,
            CreateStudentCommandHandler(
                self.student_repo,
                self.area_repo,
                self.ranking_repo,
                self.statement_repo,
                self.grade_repo,
                self.externship_repo,
                self.event_bus,
            ),
        )
        self.command_dispatcher.register(
            UpdateStudentCommand,
            UpdateStudentCommandHandler(
                self.student_repo,
                self.area_repo,
                self.ranking_repo,
                self.statement_repo,
                self.grade_repo,
                self.externship_repo,
                self.event_bus,
            ),
        )
        self.command_dispatcher.register(
            DeleteStudentCommand, DeleteStudentCommandHandler(self.student_repo)
        )
        self.command_dispatcher.register(
            MatchStudentWithOrganizationCommand,
            MatchStudentWithOrganizationCommandHandler(
                self.student_repo, self.event_bus
            ),
        )

        # Set up query dispatcher
        self.query_dispatcher = QueryDispatcher()
        self.query_dispatcher.register(
            GetStudentByIdQuery, GetStudentByIdQueryHandler(self.student_repo)
        )
        self.query_dispatcher.register(
            GetAllStudentsQuery, GetAllStudentsQueryHandler(self.student_repo)
        )
        self.query_dispatcher.register(
            GetStudentProfileQuery,
            GetStudentProfileQueryHandler(
                self.student_repo,
                self.grade_repo,
                self.statement_repo,
                self.ranking_repo,
                self.externship_repo,
            ),
        )
        self.query_dispatcher.register(
            SearchStudentsQuery, SearchStudentsQueryHandler(self.student_repo)
        )

    async def get_by_id(self, id) -> Optional[Student]:
        """Get a student by ID."""
        query = GetStudentByIdQuery(id=id)
        return await self.query_dispatcher.dispatch(query)

    async def get_all(self) -> List[Student]:
        """Get all students."""
        query = GetAllStudentsQuery()
        return await self.query_dispatcher.dispatch(query)

    async def create(self, data: Dict[str, Any]) -> Student:
        """Create a new student."""
        command = CreateStudentCommand(data=data)
        return await self.command_dispatcher.dispatch(command)

    async def create_student(self, data: Dict[str, Any]) -> Student:
        """Create a new student with the provided data"""
        command = CreateStudentCommand(data=data)
        return await self.command_dispatcher.dispatch(command)

    async def update(self, id, data: Dict[str, Any]) -> Optional[Student]:
        """Update an existing student."""
        command = UpdateStudentCommand(id=id, data=data)
        return await self.command_dispatcher.dispatch(command)

    async def update_student(self, student_id: str, data: Dict[str, Any]) -> Student:
        """Update an existing student with the provided data"""
        command = UpdateStudentCommand(id=student_id, data=data)
        return await self.command_dispatcher.dispatch(command)

    async def match_student_with_organization(
        self, student_id: str, organization_id: str, match_data: Dict[str, Any]
    ) -> None:
        """Mark a student as matched with an organization"""
        command = MatchStudentWithOrganizationCommand(
            student_id=student_id,
            organization_id=organization_id,
            match_data=match_data,
        )
        return await self.command_dispatcher.dispatch(command)

    async def delete(self, id) -> bool:
        """Delete a student."""
        command = DeleteStudentCommand(id=id)
        return await self.command_dispatcher.dispatch(command)

    async def get_student_profile(self, student_id) -> Dict[str, Any]:
        """Get complete student profile including grades, statements, etc."""
        query = GetStudentProfileQuery(student_id=student_id)
        return await self.query_dispatcher.dispatch(query)

    async def mark_as_matched(self, student_id, matched=True) -> bool:
        """Mark a student as matched or unmatched."""
        student = await self.get_by_id(student_id)
        if not student:
            return False

        return await self.update(student_id, {"is_matched": matched})

    async def search_students(self, query: str, filters: Dict = None) -> List[Student]:
        """Search students with additional filters."""
        query = SearchStudentsQuery(query=query, filters=filters)
        return await self.query_dispatcher.dispatch(query)


class CSVImportService(DomainService):
    """Service for importing students from CSV files."""

    def __init__(self):
        self.student_service = StudentService()
        self.area_repo = AreaOfLawRepository()

    def process_csv_file(self, file_path: str, imported_by=None) -> Dict[str, Any]:
        """
        Process a CSV file and import student data.

        Args:
            file_path: Path to the CSV file
            imported_by: User who initiated the import

        Returns:
            Dictionary with import results
        """
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)

            # Track results
            results = {"success_count": 0, "error_count": 0, "errors": []}

            # Process each row
            for index, row in df.iterrows():
                try:
                    with transaction.atomic():
                        # Extract basic info with safeguards
                        student_id = str(row.get("student_id", ""))
                        email = str(row.get("email", ""))

                        # Skip empty rows
                        if not student_id or not email:
                            continue

                        # Prepare student data
                        student_data = {
                            "student_id": student_id,
                            "given_names": str(row.get("given_names", "")),
                            "last_name": str(row.get("last_name", "")),
                            "email": email,
                            "program": str(row.get("program", "")),
                            "location_preferences": self._parse_list(
                                row.get("location_preferences", "")
                            ),
                            "work_preferences": self._parse_list(
                                row.get("work_preferences", "")
                            ),
                        }

                        # Check if student already exists
                        existing_student = (
                            self.student_service.student_repo.get_by_student_id(
                                student_id
                            )
                        )

                        if existing_student:
                            # Update existing student
                            self.student_service.update(
                                existing_student.id, student_data
                            )
                        else:
                            # Create new student
                            self.student_service.create(student_data)

                        results["success_count"] += 1

                except Exception as e:
                    results["error_count"] += 1
                    error_detail = f"Error processing row {index + 2}: {str(e)}"
                    results["errors"].append(error_detail)
                    logger.error(error_detail)

            return results

        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            return {
                "success_count": 0,
                "error_count": 1,
                "errors": [f"Failed to process CSV file: {str(e)}"],
            }

    def _parse_list(self, value):
        """Parse a string into a list."""
        if not value or pd.isna(value):
            return []

        return [item.strip() for item in str(value).split(";") if item.strip()]


class PDFGradeService(DomainService):
    """Service for processing student grades from PDF files."""

    def __init__(self):
        self.student_service = StudentService()
        self.grade_repo = StudentGradeRepository()

    def process_pdf_grades(self, pdf_file, student_id, grader=None) -> Dict[str, Any]:
        """
        Extract grades from a PDF file and associate with a student.

        Args:
            pdf_file: The PDF file to process
            student_id: ID of the student these grades belong to
            grader: User who uploaded the grades

        Returns:
            Dictionary with processing results
        """
        try:
            # Find the student
            student = self.student_service.student_repo.get_by_student_id(student_id)
            if not student:
                return {
                    "success": False,
                    "message": f"Student with ID {student_id} not found",
                }

            # Here we would normally use a PDF processing library to extract grades
            # For demonstration, we'll create sample grades

            grades_data = {
                "constitutional_law": "A",
                "contracts": "B+",
                "criminal_law": "A-",
                "property_law": "B",
                "torts": "A-",
                "lrw_case_brief": "A",
                "lrw_multiple_case": "B+",
                "lrw_short_memo": "A-",
            }

            # Save the PDF file
            file_content = ContentFile(pdf_file.read())

            # Check if student already has grades
            existing_grades = self.grade_repo.get_by_student(student)

            if existing_grades:
                # Update existing grades
                self.grade_repo.update(
                    existing_grades, **grades_data, grade_pdf=file_content
                )
            else:
                # Create new grades
                self.grade_repo.create(
                    student=student, **grades_data, grade_pdf=file_content
                )

            return {
                "success": True,
                "message": f"Successfully processed grades for {student.full_name}",
                "student_id": student_id,
                "grades": grades_data,
            }

        except Exception as e:
            logger.error(f"Error processing PDF grades: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to process PDF: {str(e)}",
                "student_id": student_id,
            }

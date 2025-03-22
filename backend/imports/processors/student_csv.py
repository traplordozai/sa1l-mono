import logging
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from django.db import transaction
from django.utils import timezone

from backend.students.models import Student, StudentAreaRanking
from backend.students.repositories import (StudentAreaRankingRepository,
                                           StudentRepository)

from ..models import ImportDetail
from ..repositories import ImportRepository

logger = logging.getLogger(__name__)


class StudentCsvProcessor:
    """
    Processor for student CSV imports
    """

    def __init__(self, import_log_id: str, file_path: str):
        self.import_log_id = import_log_id
        self.file_path = file_path
        self.success_count = 0
        self.error_count = 0
        self.warning_count = 0
        self.processed_count = 0
        self.errors = {}
        self.warnings = {}

        # Define column patterns to search for in CSV
        self.column_patterns = {
            "student_id": ["id", "student id", "student_id"],
            "first_name": [
                "first name",
                "firstname",
                "first",
                "given names",
                "given_names",
            ],
            "last_name": ["last name", "lastname", "last"],
            "email": ["email", "primary email"],
            "backup_email": ["backup email", "secondary email", "alternate email"],
            "program": ["program", "degree"],
            "area_1": ["area 1", "first area", "1st area", "area of law 1"],
            "area_2": ["area 2", "second area", "2nd area", "area of law 2"],
            "area_3": ["area 3", "third area", "3rd area", "area of law 3"],
            "area_4": ["area 4", "fourth area", "4th area", "area of law 4"],
            "area_5": ["area 5", "fifth area", "5th area", "area of law 5"],
            "statement_1": ["statement 1", "1st statement", "statement of interest 1"],
            "statement_2": ["statement 2", "2nd statement", "statement of interest 2"],
            "statement_3": ["statement 3", "3rd statement", "statement of interest 3"],
            "statement_4": ["statement 4", "4th statement", "statement of interest 4"],
            "statement_5": ["statement 5", "5th statement", "statement of interest 5"],
            "location_pref": ["location", "location preference", "preferred location"],
            "work_pref": ["work", "work preference", "work type", "working preference"],
        }

    def process(self) -> Dict:
        """
        Process the CSV file

        Returns:
            Dict with processing results
        """
        try:
            # Mark import as started
            ImportRepository.update_import_started(self.import_log_id)

            # Read and process the CSV
            df = self._read_csv()
            if df.empty:
                ImportRepository.update_import_failed(
                    self.import_log_id, "CSV file is empty or could not be read"
                )
                return self._get_result_dict()

            # Get column mappings
            column_map = self._get_column_map(df)

            # Validate required columns
            required_columns = ["student_id", "first_name", "last_name"]
            missing_columns = [col for col in required_columns if col not in column_map]

            if missing_columns:
                missing_names = ", ".join(missing_columns)
                ImportRepository.update_import_failed(
                    self.import_log_id, f"Missing required columns: {missing_names}"
                )
                return self._get_result_dict()

            # Process each row
            for index, row in df.iterrows():
                try:
                    self._process_row(row, column_map, index)
                except Exception as e:
                    logger.exception(f"Error processing row {index}: {str(e)}")
                    self._add_error(index, f"Error processing row: {str(e)}")

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
            logger.exception(f"Error processing student CSV: {str(e)}")
            ImportRepository.update_import_failed(self.import_log_id, str(e))
            return self._get_result_dict()

    def _read_csv(self) -> pd.DataFrame:
        """
        Read the CSV file with flexible encoding and delimiter detection
        """
        try:
            # Try utf-8 first
            return pd.read_csv(self.file_path, encoding="utf-8")
        except UnicodeDecodeError:
            # Try latin-1 if utf-8 fails
            try:
                return pd.read_csv(self.file_path, encoding="latin-1")
            except Exception as e:
                logger.error(f"Error reading CSV with latin-1 encoding: {str(e)}")
                return pd.DataFrame()  # Return empty DataFrame as fallback
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame as fallback

    def _get_column_map(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Map expected columns to actual CSV columns based on patterns
        """
        column_map = {}

        for internal_name, possible_names in self.column_patterns.items():
            # Try exact matches first
            exact_matches = [col for col in df.columns if col.lower() in possible_names]
            if exact_matches:
                column_map[internal_name] = exact_matches[0]
                continue

            # Try contains matches if no exact matches
            contains_matches = [
                col
                for col in df.columns
                if any(pattern.lower() in col.lower() for pattern in possible_names)
            ]
            if contains_matches:
                column_map[internal_name] = contains_matches[0]

        return column_map

    def _process_row(self, row, column_map, index):
        """
        Process a single row from the CSV
        """
        self.processed_count += 1

        # Extract basic info with safeguards
        student_id = str(row[column_map["student_id"]])

        # Skip empty rows
        if pd.isna(student_id) or student_id.strip() == "":
            self._add_warning(index, "Empty student ID, skipping row")
            return

        try:
            with transaction.atomic():
                # Prepare student data
                student_data = {
                    "student_id": student_id.strip(),
                }

                # Basic fields
                for field, column in [
                    ("first_name", "first_name"),
                    ("last_name", "last_name"),
                    ("email", "email"),
                    ("program", "program"),
                ]:
                    if column in column_map and not pd.isna(row[column_map[column]]):
                        student_data[field] = str(row[column_map[column]]).strip()

                # Process backup email separately for validation
                if "backup_email" in column_map and not pd.isna(
                    row[column_map["backup_email"]]
                ):
                    backup_email = str(row[column_map["backup_email"]]).strip()
                    if self._validate_email(backup_email):
                        student_data["backup_email"] = backup_email
                    else:
                        self._add_warning(
                            index, f"Invalid backup email format: {backup_email}"
                        )

                # Process location preferences
                if "location_pref" in column_map and not pd.isna(
                    row[column_map["location_pref"]]
                ):
                    locations = str(row[column_map["location_pref"]]).strip()
                    student_data["location_preferences"] = [
                        loc.strip() for loc in locations.split(";") if loc.strip()
                    ]

                # Process work preferences
                if "work_pref" in column_map and not pd.isna(
                    row[column_map["work_pref"]]
                ):
                    preferences = str(row[column_map["work_pref"]]).strip()
                    student_data["work_preferences"] = [
                        pref.strip() for pref in preferences.split(";") if pref.strip()
                    ]

                # Log original data before any processing
                original_data = {
                    key: (
                        str(row[column_map[key]])
                        if key in column_map and not pd.isna(row[column_map[key]])
                        else None
                    )
                    for key in self.column_patterns.keys()
                }

                # Create or update student
                student = StudentRepository.create_or_update_student(student_data)

                # Process area rankings
                area_rankings = []
                for i in range(1, 6):  # Areas 1-5
                    area_key = f"area_{i}"
                    if area_key in column_map and not pd.isna(
                        row[column_map[area_key]]
                    ):
                        area_name = str(row[column_map[area_key]]).strip()
                        if area_name:
                            # This would use the AreaOfLawRepository in a real implementation
                            area_rankings.append((area_name, i))

                # Save area rankings
                for area_name, rank in area_rankings:
                    StudentAreaRankingRepository.set_area_ranking(
                        student_id=student.id, area_name=area_name, rank=rank
                    )

                # Process statements
                statements = []
                for i in range(1, 6):  # Statements 1-5
                    stmt_key = f"statement_{i}"
                    if stmt_key in column_map and not pd.isna(
                        row[column_map[stmt_key]]
                    ):
                        statement = str(row[column_map[stmt_key]]).strip()
                        if statement:
                            # Would use StatementRepository in a real implementation
                            statements.append(statement)

                # Updated student_data with processed data for logging
                processed_data = student_data.copy()
                processed_data.update(
                    {
                        "id": str(student.id),
                        "area_rankings": [
                            {"area": name, "rank": rank} for name, rank in area_rankings
                        ],
                        "statements": statements,
                    }
                )

                # Log the successful import
                ImportRepository.add_import_detail(
                    import_log_id=self.import_log_id,
                    entity_type="student",
                    row_number=index,
                    original_data=original_data,
                    processed_data=processed_data,
                    status="success",
                    message=f"Successfully imported student {student.first_name} {student.last_name}",
                    entity_id=str(student.id),
                )

                self.success_count += 1

        except Exception as e:
            self._add_error(index, f"Error processing student {student_id}: {str(e)}")

            # Log the failed import
            ImportRepository.add_import_detail(
                import_log_id=self.import_log_id,
                entity_type="student",
                row_number=index,
                original_data=original_data if "original_data" in locals() else {},
                processed_data=None,
                status="error",
                message=str(e),
            )

    def _validate_email(self, email):
        """
        Basic email validation
        """
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

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

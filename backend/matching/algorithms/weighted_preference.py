# backend/matching/algorithms/weighted_preference.py
import logging
from collections import defaultdict

from django.db.models import Avg
from organizations.models import Organization
from statements.models import Statement
from students.models import Grade, Student

from .base import MatchingAlgorithm

logger = logging.getLogger(__name__)


class WeightedPreferenceAlgorithm(MatchingAlgorithm):
    """
    Implements a weighted preference matching algorithm that considers:
    - Student area of law preferences (ranks)
    - Organization area of law needs
    - Statement grades
    - Student grades
    - Location preferences
    - Work type preferences
    """

    def __init__(self, settings=None):
        self.settings = settings or {}

        # Default weights for different factors
        self.weights = {
            "area_of_law": self.settings.get("area_weight", 0.35),
            "statement": self.settings.get("statement_weight", 0.25),
            "grades": self.settings.get("grade_weight", 0.15),
            "location": self.settings.get("location_weight", 0.15),
            "work_preference": self.settings.get("work_preference_weight", 0.10),
        }

        # Verify weights sum to 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(
                f"Weights do not sum to 1.0 (total: {total_weight}). Normalizing."
            )
            for k in self.weights:
                self.weights[k] /= total_weight

        self.students = []
        self.organizations = []
        self.student_preferences = {}
        self.org_preferences = {}
        self.grades = {}
        self.statements = {}
        self.results = []

    def prepare(
        self, students, organizations, preferences, grades=None, statements=None
    ):
        """Prepare the algorithm with necessary data"""
        self.students = students
        self.organizations = organizations

        # Split preferences by type
        self.student_preferences = {
            p.student_id: {
                "areas": defaultdict(float),
                "locations": set(),
                "work_types": set(),
            }
            for p in preferences
            if p.preference_type == "STUDENT"
        }

        self.org_preferences = {
            p.organization_id: {"areas": defaultdict(float)}
            for p in preferences
            if p.preference_type == "ORGANIZATION"
        }

        # Load preferences into dictionaries for quick access
        for p in preferences:
            if p.preference_type == "STUDENT" and p.student_id:
                self.student_preferences[p.student_id]["areas"][p.area_of_law] = (
                    1.0 - ((p.rank or 5) - 1) * 0.2
                )

                # Add location and work preferences if available
                if (
                    hasattr(p.student, "location_preferences")
                    and p.student.location_preferences
                ):
                    self.student_preferences[p.student_id]["locations"] = set(
                        p.student.location_preferences
                    )

                if (
                    hasattr(p.student, "work_preferences")
                    and p.student.work_preferences
                ):
                    self.student_preferences[p.student_id]["work_types"] = set(
                        p.student.work_preferences
                    )

            elif p.preference_type == "ORGANIZATION" and p.organization_id:
                self.org_preferences[p.organization_id]["areas"][
                    p.area_of_law
                ] = p.weight

        # Store grades and statements for scoring
        self.grades = grades or {}
        self.statements = statements or {}

        return self

    def execute(self):
        """Run the matching algorithm"""
        # List to store all potential matches with scores
        potential_matches = []

        # Calculate scores for every student-organization pair
        for student in self.students:
            if student.id not in self.student_preferences:
                logger.warning(f"Student {student.id} has no preferences, skipping.")
                continue

            student_pref = self.student_preferences[student.id]
            student_grades = self.grades.get(student.id, None)

            for org in self.organizations:
                if org.id not in self.org_preferences:
                    logger.warning(
                        f"Organization {org.id} has no preferences, skipping."
                    )
                    continue

                if org.available_positions <= org.filled_positions:
                    logger.info(
                        f"Organization {org.id} has no available positions, skipping."
                    )
                    continue

                org_pref = self.org_preferences[org.id]

                # Find common areas of law
                common_areas = set(student_pref["areas"].keys()) & set(
                    org_pref["areas"].keys()
                )

                for area in common_areas:
                    # Calculate individual component scores
                    area_score = (
                        student_pref["areas"][area] + org_pref["areas"][area]
                    ) / 2

                    # Statement score if available
                    statement_score = 0.0
                    statement = self.statements.get((student.id, area), None)
                    if statement and statement.statement_grade is not None:
                        # Normalize statement grade (assumed to be 0-100)
                        statement_score = statement.statement_grade / 100.0

                    # Location preference match
                    location_score = 0.0
                    if hasattr(org, "location") and student_pref["locations"]:
                        location_score = (
                            1.0 if org.location in student_pref["locations"] else 0.0
                        )

                    # Work preference match
                    work_pref_score = 0.0
                    if (
                        hasattr(org, "work_types")
                        and student_pref["work_types"]
                        and org.work_types
                    ):
                        common_work_types = set(student_pref["work_types"]) & set(
                            org.work_types
                        )
                        work_pref_score = len(common_work_types) / max(
                            len(student_pref["work_types"]), 1
                        )

                    # Grade score
                    grade_score = 0.0
                    if student_grades:
                        # Simplified grade scoring - this would be more sophisticated in a real system
                        # Convert letter grades to numeric values (e.g. A+ = 4.3, A = 4.0, etc.)
                        grade_score = 0.85  # Simplified default value

                    # Calculate weighted total score
                    match_score = (
                        area_score * self.weights["area_of_law"]
                        + statement_score * self.weights["statement"]
                        + location_score * self.weights["location"]
                        + work_pref_score * self.weights["work_preference"]
                        + grade_score * self.weights["grades"]
                    )

                    # Store the potential match with its score
                    potential_matches.append(
                        {
                            "student_id": student.id,
                            "organization_id": org.id,
                            "area_of_law": area,
                            "match_score": match_score,
                            "components": {
                                "area_of_law_score": area_score,
                                "area_of_law_weight": self.weights["area_of_law"],
                                "statement_score": statement_score,
                                "statement_weight": self.weights["statement"],
                                "location_score": location_score,
                                "location_weight": self.weights["location"],
                                "work_preference_score": work_pref_score,
                                "work_preference_weight": self.weights[
                                    "work_preference"
                                ],
                                "grade_score": grade_score,
                                "grade_weight": self.weights["grades"],
                            },
                        }
                    )

        # Sort potential matches by score (highest first)
        potential_matches.sort(key=lambda x: x["match_score"], reverse=True)

        # Make final matches - stable matching algorithm
        # This is a simplified version - a real algorithm would be more complex
        matched_students = set()
        matched_org_positions = defaultdict(int)

        final_matches = []

        for match in potential_matches:
            student_id = match["student_id"]
            org_id = match["organization_id"]

            # Skip if student already matched
            if student_id in matched_students:
                continue

            # Find the organization
            org = next((o for o in self.organizations if o.id == org_id), None)
            if not org:
                continue

            # Skip if organization has no more positions
            if (
                matched_org_positions[org_id]
                >= org.available_positions - org.filled_positions
            ):
                continue

            # Add the match
            final_matches.append(match)
            matched_students.add(student_id)
            matched_org_positions[org_id] += 1

        self.results = final_matches
        return final_matches

    def get_results_summary(self):
        """Get summary statistics about the matching results"""
        if not self.results:
            return {
                "matched_count": 0,
                "total_students": len(self.students),
                "total_organizations": len(self.organizations),
                "average_score": 0,
            }

        scores = [match["match_score"] for match in self.results]
        return {
            "matched_count": len(self.results),
            "total_students": len(self.students),
            "total_organizations": len(self.organizations),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
        }

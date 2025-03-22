# backend/matching/algorithms/preference_priority.py
import logging
from collections import defaultdict

from .base import MatchingAlgorithm

logger = logging.getLogger(__name__)


class PreferencePriorityAlgorithm(MatchingAlgorithm):
    """
    Alternative algorithm that prioritizes exact matches on student
    preferences over score-based ranking.
    """

    def __init__(self, settings=None):
        self.settings = settings or {}
        self.students = []
        self.organizations = []
        self.student_preferences = {}
        self.org_preferences = {}
        self.statements = {}
        self.results = []

    def prepare(
        self, students, organizations, preferences, grades=None, statements=None
    ):
        """Prepare algorithm with necessary data"""
        self.students = students
        self.organizations = organizations

        # Process preferences
        self.student_preferences = {}
        self.org_preferences = {}

        for p in preferences:
            if p.preference_type == "STUDENT" and p.student_id:
                if p.student_id not in self.student_preferences:
                    self.student_preferences[p.student_id] = []

                # Store ranked preferences for student
                self.student_preferences[p.student_id].append(
                    {
                        "area_of_law": p.area_of_law,
                        "rank": p.rank
                        or 999,  # Use a high default rank if not specified
                    }
                )

            elif p.preference_type == "ORGANIZATION" and p.organization_id:
                if p.organization_id not in self.org_preferences:
                    self.org_preferences[p.organization_id] = []

                # Store organization preferences
                self.org_preferences[p.organization_id].append(
                    {"area_of_law": p.area_of_law, "weight": p.weight or 1.0}
                )

        # Sort student preferences by rank
        for student_id in self.student_preferences:
            self.student_preferences[student_id].sort(key=lambda x: x["rank"])

        # Sort organization preferences by weight (descending)
        for org_id in self.org_preferences:
            self.org_preferences[org_id].sort(key=lambda x: x["weight"], reverse=True)

        self.statements = statements or {}

        return self

    def execute(self):
        """Run the preference priority matching algorithm"""
        # Store unmatched students and organizations
        unmatched_students = list(self.students)
        available_positions = {
            org.id: max(0, org.available_positions - org.filled_positions)
            for org in self.organizations
        }

        # Maps to keep track of matches
        matches = []

        # First pass: Try to match students with their top preference
        for student in self.students:
            if student.id not in self.student_preferences:
                logger.info(f"Student {student.id} has no preferences, skipping.")
                continue

            # Get student's top preference
            top_preferences = self.student_preferences[student.id]
            if not top_preferences:
                continue

            # Try each preference in order
            for pref in top_preferences:
                area = pref["area_of_law"]

                # Find organizations with matching area and available positions
                matching_orgs = [
                    org
                    for org in self.organizations
                    if org.id in self.org_preferences
                    and any(
                        op["area_of_law"] == area for op in self.org_preferences[org.id]
                    )
                    and available_positions.get(org.id, 0) > 0
                ]

                if matching_orgs:
                    # Select the best organization based on statement grade if available
                    best_org = matching_orgs[0]
                    best_score = 0.5  # Default score

                    # Calculate a basic match score
                    if (
                        student.id in self.statements
                        and area in self.statements[student.id]
                    ):
                        statement = self.statements[student.id][area]
                        if statement.statement_grade:
                            best_score = statement.statement_grade / 100.0

                    matches.append(
                        {
                            "student_id": student.id,
                            "organization_id": best_org.id,
                            "area_of_law": area,
                            "match_score": best_score,
                            "student_rank": pref["rank"],
                        }
                    )

                    # Update available positions
                    available_positions[best_org.id] -= 1

                    # Remove student from unmatched
                    if student in unmatched_students:
                        unmatched_students.remove(student)

                    # Break after finding a match
                    break

        # Second pass: Try to match remaining students with any available organization
        for student in unmatched_students:
            if student.id not in self.student_preferences:
                continue

            # Try each area of law the student is interested in
            for pref in self.student_preferences[student.id]:
                area = pref["area_of_law"]

                # Find any organization with this area and available positions
                for org in self.organizations:
                    if (
                        org.id in available_positions
                        and available_positions[org.id] > 0
                        and org.id in self.org_preferences
                        and any(
                            op["area_of_law"] == area
                            for op in self.org_preferences[org.id]
                        )
                    ):

                        # Calculate a basic match score
                        score = 0.5  # Default score
                        if (
                            student.id in self.statements
                            and area in self.statements[student.id]
                        ):
                            statement = self.statements[student.id][area]
                            if statement.statement_grade:
                                score = statement.statement_grade / 100.0

                        matches.append(
                            {
                                "student_id": student.id,
                                "organization_id": org.id,
                                "area_of_law": area,
                                "match_score": score,
                                "student_rank": pref["rank"],
                            }
                        )

                        # Update available positions
                        available_positions[org.id] -= 1

                        # Break after finding a match
                        break

                # Break if student is matched
                if student not in unmatched_students:
                    break

        self.results = matches
        return matches

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

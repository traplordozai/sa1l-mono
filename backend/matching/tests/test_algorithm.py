# backend/matching/tests/test_algorithm.py
import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone
from matching.algorithms.base import BaseMatchingAlgorithm
from matching.algorithms.preference_based import PreferenceBasedMatching
from matching.models import Match, MatchingRound
from organizations.models import Organization
from students.models import Student


class MatchingAlgorithmTest(TestCase):
    def setUp(self):
        # Create some test students
        self.students = []
        for i in range(5):
            student = Student.objects.create(
                student_id=f"S{i + 1}",
                first_name=f"Student{i + 1}",
                last_name="Test",
                email=f"student{i + 1}@uwo.ca",
                program="JD",
            )
            self.students.append(student)

        # Create some test organizations
        self.organizations = []
        for i in range(3):
            org = Organization.objects.create(
                name=f"Organization {i + 1}",
                location=f"Location {i + 1}",
                available_positions=2,
                filled_positions=0,
            )
            self.organizations.append(org)

        # Create a matching round
        self.matching_round = MatchingRound.objects.create(
            round_number=1, status="pending"
        )

    def test_preference_based_matching(self):
        """Test that the preference-based matching algorithm works as expected"""
        algorithm = PreferenceBasedMatching()

        # Run the matching algorithm
        matches = algorithm.execute(
            students=self.students,
            organizations=self.organizations,
            matching_round=self.matching_round,
        )

        # Verify results
        self.assertEqual(
            len(matches),
            min(
                len(self.students),
                sum(org.available_positions for org in self.organizations),
            ),
        )

        # Check that each match has valid student and organization references
        for match in matches:
            self.assertIn(match.student, self.students)
            self.assertIn(match.organization, self.organizations)

            # Check that the match is associated with the correct round
            self.assertEqual(match.matching_round, self.matching_round)

            # Verify that match scores are within expected range
            self.assertGreaterEqual(match.match_score, 0)
            self.assertLessEqual(match.match_score, 100)

    def test_organization_capacity_constraints(self):
        """Test that organizations don't exceed their available positions"""
        algorithm = PreferenceBasedMatching()

        # Run the matching algorithm
        matches = algorithm.execute(
            students=self.students,
            organizations=self.organizations,
            matching_round=self.matching_round,
        )

        # Count matches per organization
        org_matches = {}
        for match in matches:
            org_id = str(match.organization.id)
            org_matches[org_id] = org_matches.get(org_id, 0) + 1

        # Verify that no organization exceeds its capacity
        for org in self.organizations:
            org_id = str(org.id)
            if org_id in org_matches:
                self.assertLessEqual(org_matches[org_id], org.available_positions)

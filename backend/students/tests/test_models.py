# backend/students/tests/test_models.py
from django.test import TestCase
from django.utils import timezone
from students.models import Student, StudentAreaRanking


class StudentModelTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_id="1234567",
            first_name="Test",
            last_name="Student",
            email="test.student@uwo.ca",
            program="JD",
            is_active=True,
        )

    def test_student_creation(self):
        """Test that a student can be created with the expected fields"""
        self.assertEqual(self.student.student_id, "1234567")
        self.assertEqual(self.student.first_name, "Test")
        self.assertEqual(self.student.last_name, "Student")
        self.assertEqual(self.student.email, "test.student@uwo.ca")
        self.assertEqual(self.student.program, "JD")
        self.assertTrue(self.student.is_active)
        self.assertFalse(self.student.is_matched)

    def test_student_full_name(self):
        """Test the full_name property"""
        self.assertEqual(self.student.full_name, "Test Student")

    def test_string_representation(self):
        """Test the string representation of a student"""
        self.assertEqual(str(self.student), "Test Student (1234567)")

    def test_profile_completion(self):
        """Test the profile_completion property"""
        # Initially all required fields are filled
        self.assertEqual(self.student.profile_completion, 100)

        # Remove a required field
        self.student.program = ""
        self.student.save()

        # Refresh from database to ensure property is recalculated
        self.student.refresh_from_db()
        self.assertLess(self.student.profile_completion, 100)

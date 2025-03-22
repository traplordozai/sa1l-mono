# backend/students/tests/test_services.py
from unittest.mock import MagicMock, patch

from core.events import StudentCreatedEvent
from django.test import TestCase
from students.models import Student
from students.services import StudentService


class StudentServiceTest(TestCase):
    def setUp(self):
        self.service = StudentService()

        # Test data
        self.student_data = {
            "student_id": "9876543",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@uwo.ca",
            "program": "JD",
        }

    @patch("core.handlers.EventBus.publish")
    def test_create_student(self, mock_publish):
        """Test creating a student through the service"""
        student = self.service.create_student(self.student_data)

        # Verify student was created with correct data
        self.assertEqual(student.student_id, "9876543")
        self.assertEqual(student.first_name, "Jane")
        self.assertEqual(student.last_name, "Doe")

        # Verify event was published
        mock_publish.assert_called_once()
        event = mock_publish.call_args[0][0]
        self.assertIsInstance(event, StudentCreatedEvent)
        self.assertEqual(event.data["student_id"], "9876543")

    @patch("core.handlers.EventBus.publish")
    def test_update_student(self, mock_publish):
        """Test updating a student through the service"""
        # First create a student
        student = self.service.create_student(self.student_data)

        # Reset mock to clear the creation event
        mock_publish.reset_mock()

        # Update the student
        updated_data = {"program": "LLM", "is_active": False}

        updated_student = self.service.update_student(str(student.id), updated_data)

        # Verify student was updated with correct data
        self.assertEqual(updated_student.program, "LLM")
        self.assertFalse(updated_student.is_active)

        # Verify event was published
        mock_publish.assert_called_once()
        event = mock_publish.call_args[0][0]
        self.assertEqual(event.data["updated_fields"], list(updated_data.keys()))

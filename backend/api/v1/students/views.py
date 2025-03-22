from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from backend.core.specifications import AndSpecification, PageSpec
from backend.students.models import Student
from backend.students.repositories import StudentRepository
from backend.students.services import StudentService
from backend.students.specifications import (StudentActiveSpecification,
                                             StudentMatchedSpecification,
                                             StudentProgramSpecification,
                                             StudentSearchSpecification)

from .serializers import StudentProfileSerializer, StudentSerializer


class StudentViewSet(viewsets.ViewSet):
    """
    API v1 endpoints for student resources
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_repository = StudentRepository()
        self.student_service = StudentService()

    def list(self, request: Request) -> Response:
        """
        Get a paginated list of students with optional filtering.

        Query parameters:
        - page: Page number (default: 1)
        - size: Page size (default: 20, max: 100)
        - search: Search term to filter students
        - program: Filter by program
        - matched: Filter by matched status (true/false)
        """
        # Get pagination parameters
        page = int(request.query_params.get("page", "1"))
        size = min(int(request.query_params.get("size", "20")), 100)
        page_spec = PageSpec(page, size)

        # Build specifications based on filters
        specs = [StudentActiveSpecification()]

        # Add search specification if provided
        search = request.query_params.get("search")
        if search:
            specs.append(StudentSearchSpecification(search))

        # Add program filter if provided
        program = request.query_params.get("program")
        if program:
            specs.append(StudentProgramSpecification(program))

        # Add matched filter if provided
        matched = request.query_params.get("matched")
        if matched is not None:
            is_matched = matched.lower() == "true"
            specs.append(StudentMatchedSpecification(is_matched))

        # Combine all specifications with AND
        combined_spec = specs[0]
        for spec in specs[1:]:
            combined_spec = AndSpecification(combined_spec, spec)

        # Get paginated results
        students, pagination = (
            self.student_repository.find_paginated_with_specification(
                combined_spec, page_spec
            )
        )

        # Serialize data
        serializer = StudentSerializer(students, many=True)

        return Response({"results": serializer.data, "pagination": pagination})

    def retrieve(self, request: Request, pk=None) -> Response:
        """Get a single student by ID"""
        student = self.student_repository.get_by_id(pk)
        if not student:
            raise Http404("Student not found")

        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def create(self, request: Request) -> Response:
        """Create a new student"""
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                student = self.student_service.create_student(serializer.validated_data)
                return Response(
                    StudentSerializer(student).data, status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, pk=None) -> Response:
        """Update an existing student"""
        student = self.student_repository.get_by_id(pk)
        if not student:
            raise Http404("Student not found")

        serializer = StudentSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                updated_student = self.student_service.update_student(
                    pk, serializer.validated_data
                )
                return Response(StudentSerializer(updated_student).data)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, pk=None) -> Response:
        """Soft-delete a student"""
        student = self.student_repository.get_by_id(pk)
        if not student:
            raise Http404("Student not found")

        self.student_service.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def get_profile(self, request: Request, pk=None) -> Response:
        """Get a student's complete profile"""
        profile = self.student_service.get_student_profile(pk)
        if not profile:
            raise Http404("Student not found")

        serializer = StudentProfileSerializer(profile)
        return Response(serializer.data)

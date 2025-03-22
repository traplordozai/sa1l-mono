import os
import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (AreaOfLaw, SelfProposedExternship, Statement, Student,
                     StudentAreaRanking, StudentGrade)
from .serializers import (AreaOfLawSerializer, ImportCSVSerializer,
                          ImportPDFSerializer,
                          SelfProposedExternshipSerializer,
                          StatementSerializer, StudentAreaRankingSerializer,
                          StudentDetailSerializer, StudentGradeSerializer,
                          StudentSerializer)
from .services import CSVImportService, PDFGradeService, StudentService


class StudentViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Student entities."""

    queryset = Student.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["program", "is_matched", "is_active", "needs_approval"]
    search_fields = ["given_names", "last_name", "email", "student_id"]
    ordering_fields = ["last_name", "created_at", "program"]
    ordering = ["last_name"]

    def get_serializer_class(self):
        """Return different serializers for different actions."""
        if self.action == "retrieve" or self.action == "profile":
            return StudentDetailSerializer
        return StudentSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ["list", "retrieve", "profile"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["get"], url_path="profile")
    def profile(self, request, pk=None):
        """Get a student's complete profile."""
        student_service = StudentService()
        profile_data = student_service.get_student_profile(pk)

        if not profile_data:
            return Response(
                {"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(profile_data["student"])
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def import_csv(self, request):
        """Import students from a CSV file."""
        serializer = ImportCSVSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        csv_file = serializer.validated_data["csv_file"]

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{csv_file.name}"
        temp_path = os.path.join(settings.MEDIA_ROOT, "uploads", unique_filename)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)

        # Save file temporarily
        with open(temp_path, "wb+") as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)

        # Process the CSV file
        csv_service = CSVImportService()
        results = csv_service.process_csv_file(
            temp_path,
            imported_by=(
                request.user.username if request.user.is_authenticated else None
            ),
        )

        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def upload_grades(self, request, pk=None):
        """Upload grades for a student."""
        student = self.get_object()

        serializer = ImportPDFSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pdf_file = serializer.validated_data["grades_pdf"]
        student_id = serializer.validated_data["student_id"]

        # Verify student ID matches
        if student.student_id != student_id:
            return Response(
                {"detail": "Student ID in request does not match the URL."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Process the PDF file
        pdf_service = PDFGradeService()
        results = pdf_service.process_pdf_grades(
            pdf_file,
            student_id,
            grader=request.user if request.user.is_authenticated else None,
        )

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def unmatched(self, request):
        """Get unmatched students."""
        student_service = StudentService()
        students = student_service.student_repo.get_unmatched_students()
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def needs_approval(self, request):
        """Get students needing approval."""
        student_service = StudentService()
        students = student_service.student_repo.get_students_needing_approval()
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)


class StudentGradeViewSet(viewsets.ModelViewSet):
    """API endpoint for managing StudentGrade entities."""

    queryset = StudentGrade.objects.all()
    serializer_class = StudentGradeSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()

        student_id = self.request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(student__student_id=student_id)

        return queryset


class StatementViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Statement entities."""

    queryset = Statement.objects.all()
    serializer_class = StatementSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["area_of_law", "statement_grade", "graded_by"]

    @action(detail=False, methods=["get"])
    def ungraded(self, request):
        """Get ungraded statements."""
        statements = self.get_queryset().filter(statement_grade__isnull=True)
        serializer = self.get_serializer(statements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def grade(self, request, pk=None):
        """Grade a statement."""
        statement = self.get_object()

        # Validate grade score
        score = request.data.get("grade")
        if not score or not isinstance(score, int) or score < 0 or score > 25:
            return Response(
                {"detail": "Grade must be an integer between 0 and 25."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the grade
        statement.statement_grade = score
        statement.graded_by = request.user
        statement.graded_at = timezone.now()
        statement.save()

        serializer = self.get_serializer(statement)
        return Response(serializer.data)


class AreaOfLawViewSet(viewsets.ModelViewSet):
    """API endpoint for managing AreaOfLaw entities."""

    queryset = AreaOfLaw.objects.all()
    serializer_class = AreaOfLawSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        """Allow read access to authenticated users."""
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class StudentAreaRankingViewSet(viewsets.ModelViewSet):
    """API endpoint for managing StudentAreaRanking entities."""

    queryset = StudentAreaRanking.objects.all()
    serializer_class = StudentAreaRankingSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "area", "rank"]


class SelfProposedExternshipViewSet(viewsets.ModelViewSet):
    """API endpoint for managing SelfProposedExternship entities."""

    queryset = SelfProposedExternship.objects.all()
    serializer_class = SelfProposedExternshipSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student"]

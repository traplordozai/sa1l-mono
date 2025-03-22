# backend/statements/views.py
import logging

from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.core.permissions import (IsAdminOrFacultyUser,
                                      IsOwnerOrAdminOrFaculty)
from backend.students.repositories import StudentRepository

from .models import AreaOfLaw, GradeImport, GradingRubric, Statement
from .repositories import (AreaOfLawRepository, GradeImportRepository,
                           GradingRubricRepository, StatementRepository)
from .serializers import (AreaOfLawSerializer, GradeImportSerializer,
                          GradeStatementSerializer, GradingRubricSerializer,
                          GradingStatisticsSerializer,
                          StatementCreateSerializer, StatementSerializer,
                          StatementUpdateSerializer)
from .services import AreaOfLawService, GradingService, StatementService

logger = logging.getLogger(__name__)


class StatementViewSet(viewsets.ModelViewSet):
    """
    API endpoints for statements.
    """

    queryset = Statement.objects.select_related("student", "area_of_law", "graded_by")
    serializer_class = StatementSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrFaculty]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "content",
        "student__first_name",
        "student__last_name",
        "area_of_law__name",
    ]
    ordering_fields = ["created_at", "updated_at", "grade", "graded_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == "create":
            return StatementCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return StatementUpdateSerializer
        elif self.action == "grade":
            return GradeStatementSerializer
        return StatementSerializer

    def get_queryset(self):
        """
        Filter statements based on user role and query parameters.
        """
        queryset = self.queryset

        # Filter by student if requested
        student_id = self.request.query_params.get("student", None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Filter by area of law if requested
        area_id = self.request.query_params.get("area_of_law", None)
        if area_id:
            queryset = queryset.filter(area_of_law_id=area_id)

        # Filter by grading status if requested
        graded = self.request.query_params.get("graded", None)
        if graded is not None:
            if graded.lower() == "true":
                queryset = queryset.filter(grade__isnull=False)
            elif graded.lower() == "false":
                queryset = queryset.filter(grade__isnull=True)

        return queryset

    def perform_create(self, serializer):
        """
        Create a new statement.
        """
        statement_service = StatementService(
            statement_repository=StatementRepository(),
            student_repository=StudentRepository(),
            area_repository=AreaOfLawRepository(),
        )

        try:
            data = serializer.validated_data
            statement = statement_service.create_statement(
                student_id=data["student"].id,
                area_id=data["area_of_law"].id,
                content=data["content"],
            )
            serializer.instance = statement
        except ValueError as e:
            logger.error(f"Error creating statement: {str(e)}")
            raise serializers.ValidationError(str(e))

    def perform_update(self, serializer):
        """
        Update an existing statement.
        """
        statement_service = StatementService(
            statement_repository=StatementRepository(),
            student_repository=StudentRepository(),
            area_repository=AreaOfLawRepository(),
        )

        try:
            statement = self.get_object()
            data = serializer.validated_data
            updated_statement = statement_service.update_statement(
                statement_id=statement.id, content=data["content"]
            )
            serializer.instance = updated_statement
        except ValueError as e:
            logger.error(f"Error updating statement: {str(e)}")
            raise serializers.ValidationError(str(e))

    def perform_destroy(self, instance):
        """
        Delete a statement.
        """
        statement_service = StatementService(
            statement_repository=StatementRepository(),
            student_repository=StudentRepository(),
            area_repository=AreaOfLawRepository(),
        )

        try:
            statement_service.delete_statement(statement_id=instance.id)
        except ValueError as e:
            logger.error(f"Error deleting statement: {str(e)}")
            raise serializers.ValidationError(str(e))

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrFacultyUser])
    def grade(self, request, pk=None):
        """
        Grade a statement.
        """
        statement = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            grading_service = GradingService(
                statement_repository=StatementRepository(),
                rubric_repository=GradingRubricRepository(),
                grade_import_repository=GradeImportRepository(),
            )

            try:
                data = serializer.validated_data
                statement = grading_service.grade_statement(
                    statement_id=statement.id,
                    grade=data["grade"],
                    grader_id=request.user.id,
                    comments=data.get("comments", ""),
                )

                return Response(
                    StatementSerializer(statement).data, status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminOrFacultyUser])
    def ungraded(self, request):
        """
        Get all ungraded statements.
        """
        statements = self.queryset.filter(grade__isnull=True)
        serializer = self.get_serializer(statements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminOrFacultyUser])
    def statistics(self, request):
        """
        Get grading statistics.
        """
        grading_service = GradingService(
            statement_repository=StatementRepository(),
            rubric_repository=GradingRubricRepository(),
            grade_import_repository=GradeImportRepository(),
        )

        stats = grading_service.get_grading_statistics()
        serializer = GradingStatisticsSerializer(stats)
        return Response(serializer.data)


class AreaOfLawViewSet(viewsets.ModelViewSet):
    """
    API endpoints for areas of law.
    """

    queryset = AreaOfLaw.objects.all()
    serializer_class = AreaOfLawSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Only allow admin to create, update, or delete areas.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def with_counts(self, request):
        """
        Get areas of law with statement counts.
        """
        area_service = AreaOfLawService(area_repository=AreaOfLawRepository())

        areas = area_service.get_areas_with_statement_count()
        return Response(areas)


class GradingRubricViewSet(viewsets.ModelViewSet):
    """
    API endpoints for grading rubrics.
    """

    queryset = GradingRubric.objects.select_related("area_of_law").prefetch_related(
        "criteria"
    )
    serializer_class = GradingRubricSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrFacultyUser]

    @action(detail=False, methods=["get"])
    def active(self, request):
        """
        Get all active grading rubrics.
        """
        rubrics = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(rubrics, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def for_area(self, request):
        """
        Get rubric for a specific area of law.
        """
        area_id = request.query_params.get("area_id", None)
        if not area_id:
            return Response(
                {"error": "area_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rubric = self.queryset.filter(area_of_law_id=area_id, is_active=True).first()
        if not rubric:
            return Response(
                {"error": f"No active rubric found for area ID {area_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(rubric)
        return Response(serializer.data)


class GradeImportViewSet(viewsets.ModelViewSet):
    """
    API endpoints for grade imports.
    """

    queryset = GradeImport.objects.select_related("imported_by")
    serializer_class = GradeImportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrFacultyUser]
    http_method_names = ["get", "post", "head", "options"]  # No update or delete

    def perform_create(self, serializer):
        """
        Create a new grade import record.
        """
        serializer.save(imported_by=self.request.user)

    @action(detail=False, methods=["post"])
    def import_file(self, request):
        """
        Import grades from a file.
        """
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES["file"]
        grading_service = GradingService(
            statement_repository=StatementRepository(),
            rubric_repository=GradingRubricRepository(),
            grade_import_repository=GradeImportRepository(),
        )

        try:
            # Save the file temporarily
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            # Process the file
            success_count, error_count, errors = (
                grading_service.import_grades_from_file(
                    file_path=temp_file_path, imported_by_id=request.user.id
                )
            )

            # Clean up
            os.unlink(temp_file_path)

            return Response(
                {
                    "message": f"Import completed: {success_count} successful, {error_count} errors",
                    "success_count": success_count,
                    "error_count": error_count,
                    "errors": errors,
                }
            )
        except Exception as e:
            logger.error(f"Error importing grades: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

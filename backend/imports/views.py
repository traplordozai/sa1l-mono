from django.core.files.uploadedfile import UploadedFile
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import ImportDetail, ImportLog, ImportStatus, ImportType
from .repositories import ImportRepository
from .serializers import ImportDetailSerializer, ImportLogSerializer
from .services import (GradesPdfImportService, OrganizationCsvImportService,
                       StatementCsvImportService, StudentCsvImportService)
from .tasks import (process_grades_pdf_task, process_organization_csv_task,
                    process_student_csv_task)


class ImportLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for import logs - read-only for security
    """

    queryset = ImportLog.objects.all().order_by("-created_at")
    serializer_class = ImportLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Admins can see all imports
        if self.request.user.is_staff:
            return ImportLog.objects.all().order_by("-created_at")

        # Regular users can only see their own imports
        return ImportLog.objects.filter(imported_by=self.request.user).order_by(
            "-created_at"
        )

    @action(detail=True, methods=["get"])
    def details(self, request, pk=None):
        """
        Get detailed records for an import
        """
        import_log = self.get_object()

        # Optional filtering by status
        status = request.query_params.get("status")
        if status:
            details = ImportDetail.objects.filter(import_log=import_log, status=status)
        else:
            details = ImportDetail.objects.filter(import_log=import_log)

        # Pagination for large imports
        page = self.paginate_queryset(details)
        if page is not None:
            serializer = ImportDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ImportDetailSerializer(details, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        """
        Get a summary of import results
        """
        import_log = self.get_object()

        # Get counts by status
        success_count = ImportDetail.objects.filter(
            import_log=import_log, status="success"
        ).count()
        error_count = ImportDetail.objects.filter(
            import_log=import_log, status="error"
        ).count()
        warning_count = ImportDetail.objects.filter(
            import_log=import_log, status="warning"
        ).count()

        return Response(
            {
                "id": str(import_log.id),
                "file_name": import_log.original_file_name,
                "import_type": import_log.import_type,
                "status": import_log.status,
                "success_count": success_count,
                "error_count": error_count,
                "warning_count": warning_count,
                "processed_count": success_count + error_count + warning_count,
                "started_at": import_log.started_at,
                "completed_at": import_log.completed_at,
                "execution_time": import_log.execution_time,
                "success_rate": import_log.success_rate,
            }
        )


class ImportViewSet(viewsets.ViewSet):
    """
    ViewSet for initiating imports
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def students(self, request):
        """
        Import students from CSV
        """
        # Check for file in request
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        # Validate file type
        if not file.name.lower().endswith(".csv"):
            return Response(
                {"error": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare import
        service = StudentCsvImportService(user=request.user)
        import_data = service.prepare_import(file)

        # Run async task
        task = process_student_csv_task.delay(
            import_data["file_path"], import_data["import_log_id"]
        )

        # Update task ID
        ImportRepository.update_task_id(import_data["import_log_id"], task.id)

        return Response(
            {
                "import_log_id": import_data["import_log_id"],
                "task_id": task.id,
                "status": "accepted",
                "message": "CSV import started",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"])
    def organizations(self, request):
        """
        Import organizations from CSV
        """
        # Check for file in request
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        # Validate file type
        if not file.name.lower().endswith(".csv"):
            return Response(
                {"error": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare import
        service = OrganizationCsvImportService(user=request.user)
        import_data = service.prepare_import(file)

        # Run async task
        task = process_organization_csv_task.delay(
            import_data["file_path"], import_data["import_log_id"]
        )

        # Update task ID
        ImportRepository.update_task_id(import_data["import_log_id"], task.id)

        return Response(
            {
                "import_log_id": import_data["import_log_id"],
                "task_id": task.id,
                "status": "accepted",
                "message": "CSV import started",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"])
    def grades(self, request):
        """
        Import student grades from PDF
        """
        # Check for file in request
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        # Validate file type
        if not file.name.lower().endswith(".pdf"):
            return Response(
                {"error": "File must be a PDF"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get optional student ID
        student_id = request.data.get("student_id")

        # Prepare import
        service = GradesPdfImportService(user=request.user)
        import_data = service.prepare_import(file, student_id)

        # Run async task
        task = process_grades_pdf_task.delay(
            import_data["file_path"],
            import_data["import_log_id"],
            import_data.get("student_id"),
        )

        # Update task ID
        ImportRepository.update_task_id(import_data["import_log_id"], task.id)

        return Response(
            {
                "import_log_id": import_data["import_log_id"],
                "task_id": task.id,
                "status": "accepted",
                "message": "PDF import started",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["get"])
    def status(self, request):
        """
        Check the status of an import
        """
        import_log_id = request.query_params.get("import_log_id")
        if not import_log_id:
            return Response(
                {"error": "import_log_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            import_log = ImportLog.objects.get(id=import_log_id)

            # Check if user has permission to view this import
            if not request.user.is_staff and import_log.imported_by != request.user:
                return Response(
                    {"error": "You do not have permission to view this import"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Return import status
            return Response(
                {
                    "id": str(import_log.id),
                    "status": import_log.status,
                    "file_name": import_log.original_file_name,
                    "import_type": import_log.import_type,
                    "processed_count": import_log.processed_count,
                    "success_count": import_log.success_count,
                    "error_count": import_log.error_count,
                    "warnings_count": import_log.warnings_count,
                    "started_at": (
                        import_log.started_at.isoformat()
                        if import_log.started_at
                        else None
                    ),
                    "completed_at": (
                        import_log.completed_at.isoformat()
                        if import_log.completed_at
                        else None
                    ),
                    "execution_time": import_log.execution_time,
                    "created_at": import_log.created_at.isoformat(),
                    "updated_at": import_log.updated_at.isoformat(),
                    "success_rate": import_log.success_rate,
                }
            )

        except ImportLog.DoesNotExist:
            return Response(
                {"error": "Import log not found"}, status=status.HTTP_404_NOT_FOUND
            )

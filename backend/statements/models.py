# backend/statements/models.py
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from backend.core.models import BaseModel
from backend.students.models import Student

User = get_user_model()


class AreaOfLaw(BaseModel):
    """
    Represents a specific area of law that students can choose for their statements.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class GradeValue:
    """
    Value object representing a grade value with validation.
    """

    MIN_GRADE = 0
    MAX_GRADE = 25

    def __init__(self, value):
        if value is not None and (value < self.MIN_GRADE or value > self.MAX_GRADE):
            raise ValueError(
                f"Grade value must be between {self.MIN_GRADE} and {self.MAX_GRADE}"
            )
        self.value = value

    def __str__(self):
        return str(self.value) if self.value is not None else "Not graded"


class Statement(BaseModel):
    """
    Represents a student's statement of interest for a specific area of law.
    """

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="statements"
    )
    area_of_law = models.ForeignKey(
        AreaOfLaw, on_delete=models.PROTECT, related_name="statements"
    )
    content = models.TextField()
    # Grading information
    grade = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(GradeValue.MIN_GRADE),
            MaxValueValidator(GradeValue.MAX_GRADE),
        ],
    )
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_statements",
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["student", "area_of_law"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.area_of_law}"

    def assign_grade(self, grade_value, grader):
        """
        Assign a grade to this statement.

        Args:
            grade_value: The numerical grade (0-25)
            grader: The User who assigned the grade
        """
        # Validate and set grade
        grade = GradeValue(grade_value).value
        self.grade = grade
        self.graded_by = grader
        self.graded_at = timezone.now()
        self.save()

        return self

    @property
    def is_graded(self):
        """Check if the statement has been graded."""
        return self.grade is not None


class GradingRubric(BaseModel):
    """
    Defines grading criteria and point allocation for statement evaluation.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    area_of_law = models.ForeignKey(
        AreaOfLaw, on_delete=models.CASCADE, related_name="rubrics"
    )
    max_points = models.IntegerField(default=25)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.area_of_law}"


class RubricCriterion(BaseModel):
    """
    Individual criterion within a grading rubric.
    """

    rubric = models.ForeignKey(
        GradingRubric, on_delete=models.CASCADE, related_name="criteria"
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    max_points = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.max_points} pts)"


class GradeImport(BaseModel):
    """
    Tracks imported grade batches (e.g., from PDF files).
    """

    imported_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="grade_imports"
    )
    file_name = models.CharField(max_length=255)
    import_date = models.DateTimeField(auto_now_add=True)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    errors = models.TextField(blank=True)

    def __str__(self):
        return f"Import on {self.import_date.strftime('%Y-%m-%d %H:%M')}"

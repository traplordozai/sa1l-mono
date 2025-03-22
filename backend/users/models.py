import uuid

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from backend.core.models import BaseModel


class UserManager(BaseUserManager):
    """
    Custom user manager that uses email as the unique identifier
    instead of username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that uses email as the username field
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    # Role fields
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    # Additional fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    @property
    def is_locked(self):
        """
        Check if the account is currently locked.
        """
        if self.account_locked_until is None:
            return False
        return timezone.now() < self.account_locked_until

    def increment_login_attempts(self):
        """
        Increment login attempts counter and lock account if necessary.
        """
        self.login_attempts += 1

        # Lock account after X failed attempts (using 5 as an example)
        if self.login_attempts >= getattr(settings, "MAX_LOGIN_ATTEMPTS", 5):
            # Lock for 30 minutes by default
            lock_minutes = getattr(settings, "ACCOUNT_LOCK_TIME_MINUTES", 30)
            self.account_locked_until = timezone.now() + timezone.timedelta(
                minutes=lock_minutes
            )

        self.save(update_fields=["login_attempts", "account_locked_until"])

    def reset_login_attempts(self):
        """
        Reset login attempts counter and remove lock.
        """
        self.login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=["login_attempts", "account_locked_until"])

    def update_last_login_ip(self, ip_address):
        """
        Update the last login IP address.
        """
        self.last_login_ip = ip_address
        self.save(update_fields=["last_login_ip"])


class Role(BaseModel):
    """
    Roles that can be assigned to users, beyond the basic Django permissions.
    This provides a more flexible way to manage permissions for different user types.
    """

    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("faculty", "Faculty Member"),
        ("student", "Student"),
        ("organization", "Organization"),
    ]

    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)

    # Permissions specific to the articling program
    can_view_all_students = models.BooleanField(default=False)
    can_edit_all_students = models.BooleanField(default=False)
    can_view_all_organizations = models.BooleanField(default=False)
    can_edit_all_organizations = models.BooleanField(default=False)
    can_run_matching = models.BooleanField(default=False)
    can_approve_matches = models.BooleanField(default=False)
    can_grade_statements = models.BooleanField(default=False)
    can_import_data = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self):
        return self.get_name_display()


class UserRole(BaseModel):
    """
    Many-to-many relationship between users and roles with additional metadata.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")

    # Additional fields
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(
        default=False, help_text=_("Primary role for this user")
    )

    class Meta:
        verbose_name = _("user role")
        verbose_name_plural = _("user roles")
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"

    def save(self, *args, **kwargs):
        """
        Override save to enforce only one primary role per user.
        """
        if self.is_primary:
            # Set all other roles for this user to not primary
            UserRole.objects.filter(user=self.user, is_primary=True).update(
                is_primary=False
            )
        super().save(*args, **kwargs)


class PasswordReset(BaseModel):
    """
    Password reset tokens and metadata.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_resets"
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    expires_at = models.DateTimeField()
    ip_requested = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("password reset")
        verbose_name_plural = _("password resets")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reset for {self.user.email}"

    @property
    def is_expired(self):
        """
        Check if the token is expired.
        """
        return timezone.now() > self.expires_at

    def mark_as_used(self):
        """
        Mark the token as used.
        """
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=["is_used", "used_at"])


class UserSession(BaseModel):
    """
    Track user sessions and activity.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("user session")
        verbose_name_plural = _("user sessions")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Session for {self.user.email}"

    def end_session(self):
        """
        End this session.
        """
        self.is_active = False
        self.ended_at = timezone.now()
        self.save(update_fields=["is_active", "ended_at"])

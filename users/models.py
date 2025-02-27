from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """
    Custom User model with additional fields:
    - role: Owner, Resident, or Admin
    - phone: User's phone number
    - workspace: ForeignKey to the Workspace model
    """

    # Roles for the user
    class Role(models.TextChoices):
        OWNER = 'owner', _('Owner')
        RESIDENT = 'resident', _('Resident')
        ADMIN = 'admin', _('Admin')

    # Fields
    # Auto-incrementing integer primary key (this is correct!)
    id = models.AutoField(primary_key=True)
    # Short, custom ID (for display/user-facing purposes)
    custom_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # Remove the old id (UUIDField)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.RESIDENT,
        verbose_name=_('Role')
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_('Email Address')
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Add related_name here
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        verbose_name=_('groups')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Add related_name here
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions')
    )
    profile_image = models.CharField(
        max_length=255,  # Store the S3 URL
        blank=True,
        null=True,
        verbose_name=_('Profile Image')
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

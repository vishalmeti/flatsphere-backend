# workspaces/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the custom User model


class Workspace(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="owned_workspaces"
    )
    timezone = models.CharField(max_length=63, default="UTC")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class UserWorkspace(models.Model):
    ROLE_CHOICES = (
        # ("owner", "Owner"),
        ("resident", "Resident"),
        ("admin", "Admin"),
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_workspaces"
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="workspace_users"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ("user", "workspace")

    def __str__(self):
        return f"{self.user.name} - {self.workspace.name} ({self.role})"


class ApartmentUnit(models.Model):
    unit_number = models.CharField(max_length=10)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="apartment_units"
    )
    rent_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    lease_start_date = models.DateField(null=True, blank=True)
    lease_end_date = models.DateField(null=True, blank=True)
    square_footage = models.IntegerField(null=True, blank=True)
    number_of_bedrooms = models.IntegerField(null=True, blank=True)
    number_of_bathrooms = models.FloatField(null=True, blank=True)
    is_occupied = models.BooleanField(default=False)

    class Meta:
        unique_together = ("unit_number", "workspace")

    def __str__(self):
        return f"{self.workspace.name} - Unit {self.unit_number}"


class UserApartment(models.Model):  # Renamed class
    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("tenant", "Tenant"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_apartments"
    )  # Updated related_name
    unit = models.ForeignKey(
        ApartmentUnit, on_delete=models.CASCADE, related_name="apartment_users"
    )  # Updated related_name
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="tenant")
    is_primary_resident = models.BooleanField(default=True)
    lease_start_date = models.DateField(null=True, blank=True)
    lease_end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "unit")
        db_table = "UserApartmentUnit"  # Keep this as the desired table name

    def __str__(self):
        return f"{self.user.custom_id} - {self.unit.workspace.name} - {self.unit.unit_number}"

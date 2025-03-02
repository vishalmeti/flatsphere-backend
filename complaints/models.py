from django.db import models
from django.conf import settings
from workspaces.models import Workspace, ApartmentUnit
from django.utils import timezone


class Complaint(models.Model):
    CATEGORY_CHOICES = (
        ("maintenance", "Maintenance"),
        ("security", "Security"),
        ("neighbor", "Neighbor Dispute"),
        ("noise", "Noise Complaint"),
        ("other", "Other"),
    )
    STATUS_CHOICES = (
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    )

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints"
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="complaints"
    )
    unit = models.ForeignKey(
        ApartmentUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Complaint"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class ComplaintMessage(models.Model):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="complaint_messages_sent",
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    message_type = models.CharField(
        max_length=20, default="text"
    )  # e.g., 'text', 'image', 'file'
    reply_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )

    class Meta:
        ordering = ["timestamp"]  # Oldest messages first (within a complaint)
        db_table = "ComplaintMessage"

    def __str__(self):
        return (
            f"From {self.sender} to complaint {self.complaint.id} at {self.timestamp}"
        )

    def save(self, *args, **kwargs):
        if self.pk:
            original = ComplaintMessage.objects.get(pk=self.pk)
            if original.content != self.content:
                self.is_edited = True
                self.edited_at = timezone.now()
        super().save(*args, **kwargs)

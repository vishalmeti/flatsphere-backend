from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Document(models.Model):
    s3_key = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents",
    )

    uploaded_on = models.DateTimeField(auto_now_add=True)
    is_profile_image = models.BooleanField(default=False)

    # Generic Foreign Key fields:
    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("object_type", "object_id")

    class Meta:
        db_table = "Document"

    def __str__(self):
        return (
            self.file_name or self.s3_key
        )  # Return filename, if present, else s3 key.

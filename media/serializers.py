# media/serializers.py
from rest_framework import serializers
from .models import Document
from django.contrib.contenttypes.models import ContentType
from django.apps import apps  # Import apps
from .helpers import S3Helper  # Import the helper function


class DocumentSerializer(serializers.ModelSerializer):
    presigned_url = serializers.SerializerMethodField()
    uploaded_by_custom_id = serializers.CharField(
        source="uploaded_by.custom_id", read_only=True
    )
    content_type_name = serializers.CharField(
        source="content_type.model", read_only=True
    )
    object_id = serializers.IntegerField()  # Allow write
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field="model",  # Use 'model' for a human-readable representation
    )

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = (
            "uploaded_by",
            "presigned_url",
            "uploaded_by_custom_id",
            "content_type_name",
        )

    def get_presigned_url(self, obj):
        return S3Helper().get_presigned_url(obj.s3_key)

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)

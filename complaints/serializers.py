# complaints/serializers.py
from rest_framework import serializers
from .models import Complaint, ComplaintMessage
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from workspaces.models import Workspace, ApartmentUnit, UserWorkspace
from media.helpers import S3Helper
from media.models import Document

User = get_user_model()


class ComplaintSerializer(serializers.ModelSerializer):
    user_custom_id = serializers.CharField(source="user.custom_id", read_only=True)
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)
    unit_number = serializers.CharField(
        source="unit.unit_number", read_only=True, allow_null=True
    )
    resolved_by_custom_id = serializers.CharField(
        source="resolved_by.custom_id", read_only=True, allow_null=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )  # Allow write
    workspace = serializers.PrimaryKeyRelatedField(
        queryset=Workspace.objects.all(), write_only=True
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=ApartmentUnit.objects.all(), required=False, allow_null=True
    )
    resolved_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Complaint
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate(self, data):
        user = data["user"]
        workspace = data["workspace"]

        if not UserWorkspace.objects.filter(user=user, workspace=workspace).exists():
            raise serializers.ValidationError(
                "The user does not belong to the specified workspace."
            )

        # If unit is provided, ensure it belongs to the workspace
        unit = data.get("unit")
        if unit and unit.workspace != workspace:
            raise serializers.ValidationError(
                "The specified unit does not belong to the given workspace."
            )
        return data


class ComplaintMessageSerializer(serializers.ModelSerializer):
    sender_custom_id = serializers.CharField(source="sender.custom_id", read_only=True)
    reply_to_content = serializers.CharField(
        source="reply_to.content", read_only=True, allow_null=True
    )
    sender = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )
    complaint = serializers.PrimaryKeyRelatedField(queryset=Complaint.objects.all())
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=ComplaintMessage.objects.all(), required=False, allow_null=True
    )
    presigned_url = serializers.SerializerMethodField()

    class Meta:
        model = ComplaintMessage
        fields = "__all__"
        read_only_fields = ("timestamp", "is_edited", "edited_at")

    def get_presigned_url(self, obj):
        contentType = ContentType.objects.get_for_model(obj)
        media_instance = Document.objects.filter(
            object_type=contentType, object_id=obj.id
        )
        urls = []
        if media_instance:
            for instance in media_instance:
                urls.append(S3Helper().get_presigned_url(instance.s3_key))
        return urls

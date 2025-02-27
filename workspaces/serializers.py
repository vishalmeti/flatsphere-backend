# workspaces/serializers.py
from rest_framework import serializers
from .models import Workspace, UserWorkspace, ApartmentUnit
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkspaceSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(
        source="owner.email", read_only=True
    )  # Keep displaying owner email
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )  # This is correct
    owner_custom_id = serializers.CharField(
        source="owner.custom_id", read_only=True
    )  # add this

    class Meta:
        model = Workspace
        fields = "__all__"
        read_only_fields = ("created_at",)


class UserWorkspaceSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    workspace = serializers.PrimaryKeyRelatedField(queryset=Workspace.objects.all())

    class Meta:
        model = UserWorkspace
        fields = "__all__"

    def validate(self, data):
        """
        Check that the user-workspace combination is unique.
        """
        user = data["user"]
        workspace = data["workspace"]

        if UserWorkspace.objects.filter(user=user, workspace=workspace).exists():
            raise serializers.ValidationError(
                "This user is already associated with this workspace."
            )
        return data


class ApartmentUnitSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)
    workspace = serializers.PrimaryKeyRelatedField(
        queryset=Workspace.objects.all()
    )  # workspace required

    class Meta:
        model = ApartmentUnit
        fields = "__all__"

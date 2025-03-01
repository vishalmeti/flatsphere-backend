# workspaces/serializers.py
from rest_framework import serializers
from .models import Workspace, UserWorkspace, ApartmentUnit, UserApartment
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
        user = data.get("user")
        workspace = data.get("workspace")

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


class UserApartmentSerializer(serializers.ModelSerializer):  # Renamed serializer
    user_custom_id = serializers.CharField(source="user.custom_id", read_only=True)
    unit_number = serializers.CharField(source="unit.unit_number", read_only=True)
    workspace_name = serializers.CharField(source="unit.workspace.name", read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    unit = serializers.PrimaryKeyRelatedField(queryset=ApartmentUnit.objects.all())

    class Meta:
        model = UserApartment
        fields = "__all__"

    def validate(self, data):
        user = data.get("user")
        unit = data.get("unit")

        # Check if user is in the workspace
        if not UserWorkspace.objects.filter(
            user=user, workspace=unit.workspace
        ).exists():
            raise serializers.ValidationError(
                "The user is not a member of the workspace."
            )

        # Primary resident check (Optional, keep if you want this functionality)
        is_primary_resident = data.get("is_primary_resident", True)
        if is_primary_resident:
            existing_primary = UserApartment.objects.filter(
                unit=unit, is_primary_resident=True
            ).exclude(pk=self.instance.pk if self.instance else None)
            if existing_primary.exists():
                raise serializers.ValidationError(
                    "There is already a primary resident for this unit."
                )

        return data

# workspaces/views.py
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action

from users.models import User

from .models import UserApartment, Workspace, UserWorkspace, ApartmentUnit
from .serializers import (
    UserApartmentSerializer,
    WorkspaceSerializer,
    UserWorkspaceSerializer,
    ApartmentUnitSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from workspaces.permissions import IsWorkspaceOwner
from workspaces.permissions import IsWorkspaceMember
from workspaces.permissions import IsOwnerOrAdmin


class WorkspaceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        print("action", self.action)
        if self.action == "create_workspace":
            permission_classes = [IsAdminUser]  # Only admins create workspaces
        elif self.action in [
            "list_workspace",
            "update_workspace",
            "delete_workspace",
        ]:
            permission_classes = [
                IsAuthenticated,
                IsWorkspaceOwner,
            ]  # Example: Owner only
        # Add more conditions for other actions as needed
        elif self.action in ["retrieve_workspace"]:
            permission_classes = [
                IsAuthenticated,
                #   IsWorkspaceMember
            ]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list_workspaces(self, request, *args, **kwargs):
        queryset = Workspace.objects.filter(
            workspace_users__user=request.user
        ) | Workspace.objects.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create_workspace(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        workspace = serializer.save()
        UserWorkspace.objects.create(
            user=request.user, workspace=workspace, role="admin"
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def retrieve_workspace(self, request, pk=None, *args, **kwargs):
        workspace = get_object_or_404(Workspace, pk=pk)
        # Check if user has access to the workspace
        if not (
            workspace.owner == request.user
            or UserWorkspace.objects.filter(
                user=request.user, workspace=workspace
            ).exists()
        ):
            return Response(
                {"detail": "No workspaces assigned to you"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(workspace)
        return Response(serializer.data)

    def update_workspace(self, request, pk=None, *args, **kwargs):
        workspace = get_object_or_404(Workspace, pk=pk)
        # Check if user has access to the workspace
        # if not (
        #     workspace.owner == request.user
        #     or UserWorkspace.objects.filter(
        #         user=request.user, workspace=workspace, role="admin"
        #     ).exists()
        # ):
        #     return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(workspace, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete_workspace(self, request, pk=None, *args, **kwargs):
        workspace = get_object_or_404(Workspace, pk=pk)
        # Check if user has access to the workspace
        if not (workspace.owner == request.user):
            return Response(
                {"detail": "You donot have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(workspace)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserWorkspaceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = UserWorkspace.objects.all()
    serializer_class = UserWorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list_user_workspaces", "retrieve_user_workspace"]:
            permission_classes = [IsAuthenticated, IsWorkspaceMember]
        elif self.action in [
            "create_user_workspace",
            "update_user_workspace",
            "delete_user_workspace",
        ]:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter based on workspace_id from URL parameter.
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id is not None:
            queryset = queryset.filter(workspace__id=workspace_id)

        # check user has access to workspace
        if workspace_id is not None:
            workspace = get_object_or_404(Workspace, pk=workspace_id)
            if not (
                workspace.owner == self.request.user
                or UserWorkspace.objects.filter(
                    user=self.request.user, workspace=workspace
                ).exists()
            ):
                return queryset.none()

            # If user is not admin or owner, can list/retrieve their own records
            if not (
                self.request.user.is_superuser or workspace.owner == self.request.user
            ):
                queryset = queryset.filter(user=self.request.user)

        return queryset

    def list_user_workspaces(self, request, workspace_id=None, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create_user_workspace(self, request, workspace_id=None, *args, **kwargs):

        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # Get workspace from URL param, and put it inside validated_data
        if workspace_id is not None:
            workspace = get_object_or_404(Workspace, pk=workspace_id)
            if isinstance(request.data, list):
                for item in serializer.validated_data:
                    item["workspace"] = workspace
            else:
                serializer.validated_data["workspace"] = workspace

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    def retrieve_user_workspace(
        self, request, workspace_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()  # Will automatically use pk from URL
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update_user_workspace(
        self, request, workspace_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()
        # check if user has permission
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response({"detail": "You do not have permission to update this."})

        # payload = [{**data, "workspace": workspace} for data in request.data]

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete_user_workspace(
        self, request, workspace_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        # check if user has permission
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response({"detail": "You do not have permission to delete this."})
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApartmentUnitViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = ApartmentUnit.objects.all()
    serializer_class = ApartmentUnitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter based on workspace_id from URL parameter.
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id is not None:
            queryset = queryset.filter(workspace__id=workspace_id)

            # check user has access to workspace
            workspace = get_object_or_404(Workspace, pk=workspace_id)
            if not (
                workspace.owner == self.request.user
                or UserWorkspace.objects.filter(
                    user=self.request.user, workspace=workspace
                ).exists()
            ):
                return queryset.none()

        return queryset

    def get_permissions(self):
        if self.action in ["list_apartment_units", "retrieve_apartment_unit"]:
            permission_classes = [IsAuthenticated]
        elif self.action in [
            "create_apartment_unit",
            "update_apartment_unit",
            "delete_apartment_unit",
        ]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list_apartment_units(self, request, workspace_id=None, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create_apartment_unit(self, request, workspace_id=None, *args, **kwargs):
        # Get workspace from URL param, and put it inside validated_data
        if workspace_id is not None:
            workspace = get_object_or_404(Workspace, pk=workspace_id)
            # check if user has permission
            if not (
                workspace.owner == self.request.user
                or UserWorkspace.objects.filter(
                    user=self.request.user, workspace=workspace, role="admin"
                ).exists()
            ):
                return Response(
                    {"detail": "You do not have permission to create this."}
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data["workspace"] = workspace

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def retrieve_apartment_unit(
        self, request, workspace_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()  # Will automatically use pk from URL
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update_apartment_unit(
        self, request, workspace_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        # check if user has permission
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response({"detail": "You do not have permission to update this."})

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete_apartment_unit(
        self, request, workspace_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        # check if user has permission
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response({"detail": "You do not have permission to delete this."})

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserApartmentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = UserApartment.objects.all()
    serializer_class = UserApartmentSerializer
    permission_classes = [IsAuthenticated]  # Basic permission

    def get_permissions(self):
        if self.action in ["list_user_apartments", "retrieve_user_apartment"]:
            permission_classes = [
                IsAuthenticated,
                IsWorkspaceMember,
            ]  # All members can see
        elif self.action in [
            "create_user_apartment",
            "update_user_apartment",
            "partial_update_user_apartment",
            "delete_user_apartment",
        ]:
            permission_classes = [
                IsAuthenticated,
                IsOwnerOrAdmin,
            ]  # Only admin and owner can create
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        workspace_id = self.kwargs.get("workspace_id")
        unit_id = self.kwargs.get("unit_id")

        if not workspace_id:
            return UserApartment.objects.none()  # Must have a workspace

        # Get Workspace and check permissions
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not (
            self.request.user.is_superuser
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace
            ).exists()
        ):
            return UserApartment.objects.none()  # User not in workspace

        # Filter by workspace
        queryset = queryset.filter(unit__workspace_id=workspace_id)

        # Further filter by unit_id if provided
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)

        # If not admin/owner, restrict to own records.
        if not (
            self.request.user.is_superuser
            or Workspace.objects.filter(
                pk=workspace_id, owner=self.request.user
            ).exists()
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace_id=workspace_id, role="admin"
            ).exists()
        ):
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def list_user_apartments(
        self, request, workspace_id=None, unit_id=None, *args, **kwargs
    ):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create_user_apartment(
        self, request, workspace_id=None, unit_id=None, *args, **kwargs
    ):
        # workspace and unit id validation.
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response(
                {
                    "detail": "You do not have permission to create user_apartment in this workspace."
                }
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["unit"] = get_object_or_404(
            ApartmentUnit, pk=serializer.validated_data["unit"].id, workspace=workspace
        )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    # def retrieve_user_apartment(
    #     self, request, workspace_id=None, unit_id=None, pk=None, *args, **kwargs
    # ):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

    # def update_user_apartment(
    #     self, request, workspace_id=None, unit_id=None, pk=None, *args, **kwargs
    # ):
    #     instance = self.get_object()
    #     workspace = get_object_or_404(Workspace, pk=workspace_id)
    #     if not (
    #         workspace.owner == self.request.user
    #         or UserWorkspace.objects.filter(
    #             user=self.request.user, workspace=workspace, role="admin"
    #         ).exists()
    #     ):
    #         return Response(
    #             {"detail": "You do not have permission to update this user apartment."}
    #         )
    #     serializer = self.get_serializer(instance, data=request.data, partial=False)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.validated_data["unit"] = get_object_or_404(
    #         ApartmentUnit, pk=serializer.validated_data["unit"].id, workspace=workspace
    #     )
    #     self.perform_update(serializer)
    #     return Response(serializer.data)

    # def partial_update_user_apartment(
    #     self, request, workspace_id=None, unit_id=None, pk=None, *args, **kwargs
    # ):
    #     instance = self.get_object()
    #     workspace = get_object_or_404(Workspace, pk=workspace_id)
    #     if not (
    #         workspace.owner == self.request.user
    #         or UserWorkspace.objects.filter(
    #             user=self.request.user, workspace=workspace, role="admin"
    #         ).exists()
    #     ):
    #         return Response(
    #             {"detail": "You do not have permission to update this user apartment."}
    #         )

    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.validated_data["unit"] = get_object_or_404(
    #         ApartmentUnit, pk=serializer.validated_data["unit"].id, workspace=workspace
    #     )
    #     self.perform_update(serializer)
    #     return Response(serializer.data)

    # def perform_update(self, serializer):
    #     serializer.save()

    def delete_user_apartment(
        self, request, workspace_id=None, unit_id=None, pk=None, *args, **kwargs
    ):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        unit = request.data.get("unit")
        user = request.data.get("user")

        userInstance = get_object_or_404(User, pk=user)
        unitInstance = get_object_or_404(ApartmentUnit, pk=unit)
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response(
                {
                    "detail": "You do not have permission to delete this user from apartment."
                }
            )
        instance = UserApartment.objects.get(user=userInstance, unit_id=unitInstance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

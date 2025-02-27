# workspaces/views.py
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from .models import Workspace, UserWorkspace, ApartmentUnit
from .serializers import (
    WorkspaceSerializer,
    UserWorkspaceSerializer,
    ApartmentUnitSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404


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
        if self.action == "create_workspace":
            permission_classes = [IsAdminUser]
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
            user=request.user, workspace=workspace, role="owner"
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
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(workspace)
        return Response(serializer.data)

    def update_workspace(self, request, pk=None, *args, **kwargs):
        workspace = get_object_or_404(Workspace, pk=pk)
        # Check if user has access to the workspace
        if not (
            workspace.owner == request.user
            or UserWorkspace.objects.filter(
                user=request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(workspace, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete_workspace(self, request, pk=None, *args, **kwargs):
        workspace = get_object_or_404(Workspace, pk=pk)
        # Check if user has access to the workspace
        if not (workspace.owner == request.user):
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
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
            permission_classes = [IsAuthenticated]
        elif self.action in [
            "create_user_workspace",
            "update_user_workspace",
            "delete_user_workspace",
        ]:
            permission_classes = [IsAuthenticated]
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

        serializer = self.get_serializer(instance, data=request.data, partial=True)
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

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .models import Complaint, ComplaintMessage
from .serializers import ComplaintSerializer, ComplaintMessageSerializer
from rest_framework.permissions import IsAuthenticated
from workspaces.permissions import (
    IsWorkspaceMember,
    IsOwnerOrAdmin,
)  # Import your permissions
from workspaces.models import Workspace, UserWorkspace, ApartmentUnit
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.contrib.contenttypes.models import ContentType
from media.models import Document  # Import
from media.serializers import DocumentSerializer  # Import


class ComplaintViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            # All workspace members can create/list/view
            permission_classes = [IsAuthenticated, IsWorkspaceMember]
        elif self.action in ["update", "partial_update", "destroy", "resolve"]:
            permission_classes = [
                IsAuthenticated,
                # IsOwnerOrAdmin,
            ]  # Only admin/owner can update/delete/resolve
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        workspace_id = self.kwargs.get("workspace_id")

        if not workspace_id:
            return Complaint.objects.none()

        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not (
            self.request.user.is_superuser
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace
            ).exists()
        ):
            return Complaint.objects.none()

        queryset = queryset.filter(workspace=workspace)

        # Further restrict based on user role, if not admin/owner.
        if not (
            self.request.user.is_superuser
            or Workspace.objects.filter(
                pk=workspace_id, owner=self.request.user
            ).exists()
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            queryset = queryset.filter(
                user=self.request.user
            )  # Only show own complaints

        return queryset

    def list(self, request, workspace_id=None, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, workspace_id=None, *args, **kwargs):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["workspace"] = workspace
        serializer.validated_data["user"] = request.user  # Set the user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, workspace_id=None, pk=None, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, workspace_id=None, pk=None, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, workspace_id=None, pk=None, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, workspace_id=None, pk=None, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated, IsOwnerOrAdmin],
    )
    def resolve(self, request, workspace_id=None, pk=None):
        """Marks a complaint as resolved."""
        complaint = self.get_object()
        complaint.status = "resolved"
        complaint.save()
        serializer = self.get_serializer(complaint)
        return Response(serializer.data)


class ComplaintMessageViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = ComplaintMessage.objects.all()
    serializer_class = ComplaintMessageSerializer
    permission_classes = [IsAuthenticated]  # Basic permission

    def get_permissions(self):
        if self.action in ["list_messages", "retrieve_message"]:
            permission_classes = [
                IsAuthenticated,
                IsWorkspaceMember,
            ]  # All members can see
        elif self.action in [
            "create_message",
            "update_message",
            "partial_update_message",
            "delete_message",
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
        complaint_id = self.kwargs.get("complaint_id")  # Get complaint id from url

        if not workspace_id:
            return ComplaintMessage.objects.none()

        # Get Workspace and check permissions
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not (
            self.request.user.is_superuser
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace
            ).exists()
        ):
            return ComplaintMessage.objects.none()  # User not in workspace

        # Filter by workspace
        queryset = queryset.filter(complaint__workspace_id=workspace_id)

        # Further filter by complaint_id if provided
        if complaint_id:
            queryset = queryset.filter(complaint_id=complaint_id)

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
            queryset = queryset.filter(sender=self.request.user)

        return queryset

    @action(detail=False, methods=["GET"], url_path="list")  # Changed URL path
    def list_messages(
        self, request, workspace_id=None, complaint_id=None, *args, **kwargs
    ):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"], url_path="create")  # Changed URL path
    def create_message(self, request, workspace_id=None, complaint_id=None):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        # Check if user has access to workspace and complaint.
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace
            ).exists()
        ):
            return Response(
                {
                    "detail": "You do not have permission to create a message in this complaint."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["complaint"] = get_object_or_404(
            Complaint, pk=complaint_id, workspace=workspace
        )
        serializer.validated_data["sender"] = request.user

        message = serializer.save()  # Save to get the message ID

        # Handle file uploads, if any, *after* saving the message
        if "message_type" in request.data and request.data["message_type"] in (
            "image",
            "file",
        ):
            if "file" not in request.FILES:
                return Response(
                    {"detail": "Missing 'file' for image/file message type."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            uploaded_file = request.FILES["file"]
            # Determine content type, use it to create Document
            content_type_str = request.data.get("content_type_str")
            if not content_type_str:
                return Response(
                    {
                        "detail": "Missing 'content_type_str' for image/file message type."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            content_type = get_object_or_404(
                ContentType, model=content_type_str.lower()
            )  # complaintmessage, document etc
            document = Document.objects.create(
                file=uploaded_file,
                uploaded_by=request.user,
                content_type=content_type,
                object_id=message.id,  # Associate with the *message*
                file_name=uploaded_file.name,  # Set filename.
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["GET"], url_path="retrieve")  # Added url path
    def retrieve_message(
        self, request, workspace_id=None, complaint_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT"], url_path="update")  # Added url path
    def update_message(
        self, request, workspace_id=None, complaint_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response(
                {"detail": "You do not have permission to update this message."}
            )

        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=["PATCH"], url_path="partial-update")  # Added url path
    def partial_update_message(
        self, request, workspace_id=None, complaint_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response(
                {"detail": "You do not have permission to update this message."}
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=["DELETE"], url_path="delete")  # Changed URL path
    def delete_message(
        self, request, workspace_id=None, complaint_id=None, pk=None, *args, **kwargs
    ):
        instance = self.get_object()
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not (
            workspace.owner == self.request.user
            or UserWorkspace.objects.filter(
                user=self.request.user, workspace=workspace, role="admin"
            ).exists()
        ):
            return Response(
                {"detail": "You do not have permission to delete this message."}
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

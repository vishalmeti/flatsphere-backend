# workspaces/permissions.py

from rest_framework import permissions
from workspaces.models import Workspace, UserWorkspace
from django.shortcuts import get_object_or_404


class IsWorkspaceOwner(permissions.BasePermission):
    """
    ✅ Custom permission to only allow owners of a workspace to access it.
    """

    def has_object_permission(self, request, view, obj):
        # obj here is the *Workspace* instance
        return obj.owner == request.user


class IsWorkspaceAdmin(permissions.BasePermission):
    """
    ✅ Custom permission to only allow admin of workspace to access
    """

    def has_permission(self, request, view):
        workspace_id = view.kwargs.get("workspace_id")
        if not workspace_id:
            return False

        # Check if user is admin in workspace.
        return UserWorkspace.objects.filter(
            user=request.user, workspace_id=workspace_id, role="admin"
        ).exists()


class IsWorkspaceMember(permissions.BasePermission):
    """
    ✅ Custom permission to only allow members of a workspace to access it.
    """

    def has_permission(self, request, view):
        workspace_id = view.kwargs.get("workspace_id")  # Get workspace id from url
        if not workspace_id:  # If workspace id not present.
            return False

        # Check if the user is associated with the workspace
        return UserWorkspace.objects.filter(
            user=request.user, workspace_id=workspace_id
        ).exists()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    ✅ Custom permission to allow access only to workspace owner and admin.
    """

    def has_permission(self, request, view):
        workspace_id = view.kwargs.get("workspace_id")
        if not workspace_id:
            return False

        workspace = get_object_or_404(Workspace, pk=workspace_id)
        # Check if user is workspace owner or admin.
        return (
            workspace.owner == request.user
            or UserWorkspace.objects.filter(
                user=request.user, workspace=workspace, role="admin"
            ).exists()
        )

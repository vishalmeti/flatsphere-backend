# complaints/urls.py
from django.urls import path
from . import views


"""

Resulting URL Structure:

This configuration will result in the following URL structure:

Complaints:

GET /api/v1/complaints/workspaces/{workspace_id}/complaints/ (List)
POST /api/v1/complaints/workspaces/{workspace_id}/complaints/ (Create)
GET /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/ (Retrieve)
PUT /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/ (Update)
PATCH /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/ (Partial Update)
DELETE /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/ (Delete)
POST /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/resolve/ (Resolve)
Complaint Messages:

GET /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/messages/ (List - list_messages)
POST /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/messages/ (Create -create_message)
GET /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/messages/{message_id}/ (Retrieve, Update, Delete)
PUT /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/messages/{message_id}/
PATCH /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/messages/{message_id}/
DELETE /api/v1/complaints/workspaces/{workspace_id}/complaints/{complaint_id}/messages/{message_id}/


"""


urlpatterns = [
    # Complaints (nested under workspaces)
    path(
        "workspaces/<int:workspace_id>/complaints/",
        views.ComplaintViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<int:workspace_id>/complaints/<int:pk>/",
        views.ComplaintViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "workspaces/<int:workspace_id>/complaints/<int:pk>/resolve/",
        views.ComplaintViewSet.as_view({"post": "resolve"}),
    ),
    # Complaint Messages (nested under complaints)
    path(
        "workspaces/<int:workspace_id>/complaints/<int:complaint_id>/messages/",
        views.ComplaintMessageViewSet.as_view(
            {"get": "list_messages", "post": "create_message"}
        ),
    ),
    path(
        "workspaces/<int:workspace_id>/complaints/<int:complaint_id>/messages/<int:pk>/",
        views.ComplaintMessageViewSet.as_view(
            {
                "get": "retrieve_message",
                "put": "update_message",
                "patch": "partial_update_message",
                "delete": "delete_message",
            }
        ),
    ),
]

# complaints/urls.py
from django.urls import path
from . import views

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

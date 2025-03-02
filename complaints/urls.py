# complaints/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Complaints
    path(
        "complaints/", views.ComplaintViewSet.as_view({"get": "list", "post": "create"})
    ),
    path(
        "complaints/<int:pk>/",
        views.ComplaintViewSet.as_view(
            {
                "get": "retrieve",
                # "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "complaints/<int:pk>/resolve/",
        views.ComplaintViewSet.as_view(
            {"post": "resolve"}  # Custom action for resolving
        ),
    ),
    # Complaint Messages (nested under complaints)
    path(
        "complaints/<int:complaint_id>/messages/",
        views.ComplaintMessageViewSet.as_view(
            {"get": "list_messages", "post": "create_message"}
        ),
    ),
    path(
        "complaints/<int:complaint_id>/messages/<int:pk>/",
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

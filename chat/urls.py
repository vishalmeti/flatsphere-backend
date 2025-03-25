# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Conversations (list, retrieve, delete)
    path(
        "conversations/",
        views.ConversationViewSet.as_view(
            {
                "get": "list",
            }
        ),
    ),
    # New endpoint to get conversation by recipient ID
    path(
        "conversations/recipient/<int:recipient_id>/",
        views.ConversationViewSet.as_view({"get": "get_by_recipient"}),
    ),
    path(
        "conversations/<int:pk>/",
        views.ConversationViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
    ),
    # Messages (list, create, retrieve, update, delete)
    path("messages/", views.MessageViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "messages/<int:pk>/",
        views.MessageViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
]

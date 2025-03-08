# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Conversations
    path('', views.ConversationViewSet.as_view({
        'get': 'list',
    })),
    path('<int:pk>/', views.ConversationViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'  # Add DELETE for completeness
    })),

    # Messages (nested under conversations)
    path('<int:conversation_pk>/messages/', views.MessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('<int:conversation_pk>/messages/<int:pk>/', views.MessageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
]
from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet,FileUploadView

# ...existing code...
router = routers.SimpleRouter()
# ...existing code...

urlpatterns = [
    path('users/', UserViewSet.as_view({
        'get': 'list',
        'post': 'create_user',
        'patch': 'bulk_update_users',
        'delete': 'bulk_delete_users'
    })),
    path('users/<str:email>/', UserViewSet.as_view({
        'get': 'retrieve_user',
        'patch': 'update_user',
        'delete': 'delete_user'
    })),
    path('upload/', FileUploadView.as_view({
        'post': 'upload_file'
    })),


]

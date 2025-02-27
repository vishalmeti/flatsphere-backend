from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet,FileUploadView

# ...existing code...
router = routers.SimpleRouter()
# ...existing code...

urlpatterns = [
    path(
        "",
        UserViewSet.as_view(
            {
                "get": "list",
                "post": "create_user",
                "patch": "bulk_update_users",
                "delete": "bulk_delete_users",
            }
        ),
    ),
    ## add it before the path("<str:email>/", UserViewSet because it will be matched first
    path("profile/", FileUploadView.as_view({"post": "upload_file"})),
    path(
        "<str:email>/",
        UserViewSet.as_view(
            {"get": "retrieve_user", "patch": "update_user", "delete": "delete_user"}
        ),
    ),
]

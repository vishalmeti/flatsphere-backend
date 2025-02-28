# media/urls.py
from django.urls import path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()

urlpatterns = [
    path(
        "",
        views.FileUploadView.as_view({"post": "upload_file"}),
        name="presigned_url",
    ),
]

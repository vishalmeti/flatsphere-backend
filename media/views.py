from django.shortcuts import render

from media.models import Document
from media.serializers import DocumentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from users.authentication import CustomJWTAuthentication
from django.core.exceptions import ValidationError
from .helpers import S3Helper  # Import the helper function
from django.contrib.contenttypes.models import ContentType
from decouple import config


# Create your views here.
# Example of media app view:


class FileUploadView(viewsets.ModelViewSet):
    authentication_classes = [CustomJWTAuthentication]  # Enforce JWT authentication
    permission_classes = [IsAuthenticated]

    def validate_image(self, file):
        valid_mime_types = ["image/jpeg", "image/png", "image/gif"]
        if file.content_type not in valid_mime_types:
            raise ValidationError(
                "Unsupported file type. Only JPEG, PNG, and GIF are allowed."
            )

    def upload_file(self, request, *args, **kwargs):
        if "file" not in request.data:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get the uploaded file from request.data
        file = request.data.get("file")
        objectId = request.data.get("objectId")
        modelName = request.data.get("modelName")
        isProfile = request.data.get("isProfile") or False

        contentType = ContentType.objects.get(model=modelName)

        # Validate the file type
        try:
            self.validate_image(file)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Ensure the file name is a string
        try:
            file_extension = file.name.split(".")[-1]
            file_name = (
                contentType.model + "/" + objectId + "/" + file.name
                if not isProfile
                else "profiles/" + request.user.username + "_profile." + file_extension
            )

            # Save the file to the server
            file_url, message = S3Helper().upload_to_s3(
                file_name, file, config("AWS_STORAGE_BUCKET_NAME")
            )
            if file_url:
                user = request.user
                # user.profile_image = file_url

                document = Document.objects.create(
                    object_id=objectId,
                    object_type=contentType,
                    uploaded_by=user,
                    s3_key=file_name,
                    file_name=file.name,
                    is_profile_image=isProfile,
                )
                document.save()

                user.save()
                return Response(
                    {"message": message, "file_url": file_url},
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            return Response(
                {"error": message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_presigned_url(self, objId):
        obj = Document.objects.get(id=objId)
        return S3Helper().get_presigned_url(obj.s3_key)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]  # Example permission

    def get_queryset(self):
        # Example: Filter documents based on the related object
        # You would likely add more sophisticated filtering based on your needs.
        content_type_str = self.request.query_params.get("content_type")
        object_id = self.request.query_params.get("object_id")

        queryset = super().get_queryset()

        if content_type_str and object_id:
            try:
                content_type = ContentType.objects.get(model=content_type_str)
                queryset = queryset.filter(
                    content_type=content_type, object_id=object_id
                )
            except ContentType.DoesNotExist:
                return Document.objects.none()  # Or raise an exception

        # Further filtering based on permissions, etc.
        return queryset

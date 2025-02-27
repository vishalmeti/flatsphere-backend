from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from decouple import config
# from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from .authentication import CustomJWTAuthentication
from django.contrib.auth.hashers import make_password

import boto3
from botocore.exceptions import NoCredentialsError

from .helpers import S3Helper  # Import the helper function

# views.py

from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.conf import settings

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [CustomJWTAuthentication]  # Enforce JWT authentication
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    @action(detail=False, methods=['get'])
    def list(self, request):
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        data = request.data
        if not isinstance(data["users"], list):
            return Response({"error": "Expected a list of users credentials"}, status=status.HTTP_400_BAD)
        # for user_data in data["users"]:
        #     user_data['password'] = make_password(user_data['password'])

        serializer = UserSerializer(data=data["users"], many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def update_user(self, request, email=None):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_user(self, request, email=None):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def retrieve_user(self, request, email=None):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def bulk_update_users(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Expected a list of user data"}, status=status.HTTP_400_BAD_REQUEST)

        updated_users = []
        for user_data in data:
            try:
                user = User.objects.get(pk=user_data.get("id"))
                serializer = UserSerializer(user, data=user_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_users.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": f"User with id {user_data.get('id')} not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(updated_users, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def bulk_delete_users(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({"error": "Expected a list of user IDs"}, status=status.HTTP_400_BAD_REQUEST)

        users_to_delete = User.objects.filter(id__in=ids)
        if users_to_delete.count() != len(ids):
            return Response({"error": "One or more users not found"}, status=status.HTTP_404_NOT_FOUND)

        users_to_delete.delete()
        return Response({"message": "Bulk delete successful"}, status=status.HTTP_204_NO_CONTENT)


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
        if 'file' not in request.data:
            return Response(
                {'error': 'No file uploaded'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the uploaded file from request.data
        file = request.data['file']
        # Validate the file type
        try:
            self.validate_image(file)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Ensure the file name is a string
        try:
            file_extension = file.name.split(".")[-1]
            file_name = (
                "profiles/" + request.user.username + "_profile." + file_extension
            )

            # Save the file to the server
            file_url, message = S3Helper().upload_to_s3(
                file_name, file, config("AWS_STORAGE_BUCKET_NAME")
            )
            if file_url:
                user = request.user
                user.profile_image = file_url
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
            return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create your views here.

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .models import ChatMessage, Conversation
from .serializers import (
    MessageSerializer,
    ConversationSerializer,
)
from rest_framework.permissions import IsAuthenticated
from workspaces.models import Workspace, UserWorkspace
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from media.models import Document

User = get_user_model()


class ConversationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]  # Or more specific permissions

    def get_queryset(self):
        """
        Lists conversations for the current user.
        """
        user = self.request.user
        # Get conversations where the user is either user1 or user2
        return Conversation.objects.filter(Q(user1=user) | Q(user2=user)).distinct()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, pk=None, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, pk=None, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class MessageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ChatMessage.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]  # Or more specific permissions

    def get_queryset(self):
        """
        Filter messages by conversation ID.
        """
        conversation_id = self.kwargs.get("conversation_pk")  # From URL
        if conversation_id:
            return ChatMessage.objects.filter(conversation_id=conversation_id)
        return ChatMessage.objects.none()  # Or raise a 404, depending on your needs.

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # 1. Get the sender (current user) and recipient (from request data).
        
        sender = request.user
        recipient_id = request.data.get("recipient")  # Assuming you send recipient's ID
        if not recipient_id:
            return Response(
                {"detail": "A recipient ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            recipient = User.objects.get(pk=recipient_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Recipient user not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Check if a conversation already exists.
        conversation = Conversation.objects.filter(
            Q(user1=sender, user2=recipient) | Q(user1=recipient, user2=sender)
        ).first()  # Use .first() to get a single object or None

        # 3. Create a conversation if it doesn't exist.
        if not conversation:
            conversation = Conversation.objects.create(user1=sender, user2=recipient)

        # 4. Now that you *definitely* have a conversation, create the message.
        payload = request.data.copy()
        payload["sender"] = sender.id
        payload["conversation"] = conversation.id
        serializer = self.get_serializer
        serializedData = serializer(data=payload)
        if not serializedData.is_valid():
            return Response(
                serializedData.errors, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            serializedData.save()  # Save to get the message ID

            # 5. Update last_message_at on Conversation
            conversation.last_message_at = timezone.now()
            conversation.save()

            return Response(
                serializedData.data, status=status.HTTP_201_CREATED, 
            )

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, pk=None, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, pk=None, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, pk=None, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, pk=None, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .models import ChatMessage, Conversation  # Import Conversation
from .serializers import (
    MessageSerializer,
    ConversationSerializer,
)  # You'll need a MessageSerializer
from rest_framework.permissions import IsAuthenticated
from workspaces.models import Workspace, UserWorkspace  # Import models
from django.shortcuts import get_object_or_404
from django.db.models import Q  # Import Q objects
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
        # return super().destroy(request, *args, **kwargs)
        conversation = get_object_or_404(Conversation, pk=pk)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_by_recipient(self, request, recipient_id=None):
        """
        Get a conversation by recipient user ID.
        """
        user = request.user

        try:
            recipient = User.objects.get(pk=recipient_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Recipient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        conversation = Conversation.objects.filter(
            Q(user1=user, user2=recipient) | Q(user1=recipient, user2=user)
        ).first()

        if not conversation:
            return Response(
                {"detail": "No conversation found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)


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
        queryset = super().get_queryset()
        recipient_id = self.request.query_params.get("recipient_id")
        user = self.request.user

        if recipient_id:
            try:
                recipient = User.objects.get(pk=recipient_id)
            except User.DoesNotExist:
                return ChatMessage.objects.none()  # Or raise a 404

            # Find the conversation between the current user and the recipient
            conversation = Conversation.objects.filter(
                Q(user1=user, user2=recipient) | Q(user1=recipient, user2=user)
            ).first()

            if conversation:
                queryset = queryset.filter(conversation=conversation)
            else:
                queryset = ChatMessage.objects.none()  # No conversation exists

        # Added additional security, so that user can only see conversations that they are part of.
        queryset = queryset.filter(
            Q(sender=self.request.user)
            | Q(conversation__user1=self.request.user)
            | Q(conversation__user2=self.request.user)
        )
        return queryset

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # 1. Get the sender (current user) and recipient (from request data).
        sender = request.user
        recipient_id = request.data.get("recipient")
        conversation_id = request.data.get("conversation")  # Get conversation ID
        content = request.data.get("content")
        reply_to_id = request.data.get("reply_to")  # Get reply_to ID

        # Check if an existing conversation ID is provided
        if conversation_id:
            try:
                conversation = Conversation.objects.get(pk=conversation_id)
                # Verify that the current user is part of the conversation
                if sender != conversation.user1 and sender != conversation.user2:
                    return Response(
                        {"detail": "You are not part of this conversation."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Conversation.DoesNotExist:
                return Response(
                    {"detail": "Conversation not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # No existing conversation ID, proceed with recipient check and conversation creation
            if not recipient_id:
                return Response(
                    {
                        "detail": "A recipient ID is required to start a new conversation."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                recipient = User.objects.get(pk=recipient_id)
            except User.DoesNotExist:
                return Response(
                    {"detail": "Recipient user not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            conversation = Conversation.objects.filter(
                Q(user1=sender, user2=recipient) | Q(user1=recipient, user2=sender)
            ).first()

            if not conversation:
                conversation = Conversation.objects.create(
                    user1=sender, user2=recipient
                )
        payload = {
            "content": content,
            "conversation": conversation.id,
            "reply_to": reply_to_id,
        }
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["sender"] = sender  # Set sender
        serializer.save()

        conversation.last_message_at = timezone.now()
        conversation.save()

        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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

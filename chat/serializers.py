# chat/serializers.py
from rest_framework import serializers
from .models import ChatMessage, Conversation
from django.contrib.auth import get_user_model
from media.serializers import DocumentSerializer

User = get_user_model()

class ConversationSerializer(serializers.ModelSerializer):
    user1_username = serializers.CharField(source='user1.username', read_only=True)
    user2_username = serializers.CharField(source='user2.username', read_only=True)
    user1_custom_id = serializers.CharField(source='user1.custom_id', read_only=True)
    user2_custom_id = serializers.CharField(source='user2.custom_id', read_only=True)

    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = ('created_at', 'last_message_at')


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_custom_id = serializers.CharField(source='sender.custom_id', read_only=True)
    conversation_id = serializers.IntegerField(source='conversation.id', read_only=True)
    reply_to_content = serializers.CharField(source='reply_to.content', read_only=True, default=None)
    # documents = DocumentSerializer(many=True, read_only=True) # Add this

    # sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required = False) # No need, we are setting in view.
    # conversation = serializers.PrimaryKeyRelatedField(queryset=Channel.objects.all()) # No need to set in request payload.
    reply_to = serializers.PrimaryKeyRelatedField(queryset=ChatMessage.objects.all(), required=False, allow_null=True)
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ('timestamp', 'is_edited', 'edited_at')
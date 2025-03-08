# chat/models.py
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from media.models import Document
from django.utils import timezone


class Conversation(models.Model):
    """
    Represents a one-on-one conversation between two users.
    """
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations2')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True) #For sorting.

    class Meta:
        # Enforce uniqueness:  A pair of users can only have ONE conversation.
        unique_together = ('user1', 'user2')
        ordering = ['-last_message_at'] # Order by last message time
        db_table = "Conversation"

    def __str__(self):
        return f"Conversation between {self.user1.username} and {self.user2.username}"

    def get_other_user(self, user):
        """
        Returns the *other* user in the conversation, given one user.
        """
        if user == self.user1:
            return self.user2
        elif user == self.user2:
            return self.user1
        else:
            return None  # Or raise an exception if the user is not part of the conversation.

    def save(self, *args, **kwargs):
      if self.pk:
          original = Conversation.objects.get(pk=self.pk)
          if (original.user1 != self.user1) or (original.user2 != self.user2):
              # Check for existing conversation in reverse order
              existing_convo = Conversation.objects.filter(user1=self.user2, user2=self.user1).first()
              if existing_convo:
                  raise ValueError("A conversation already exists between these users (in reverse order).")
      else:
           existing_convo = Conversation.objects.filter(user1=self.user2, user2=self.user1).first()
           if existing_convo:
              raise ValueError("A conversation already exists between these users (in reverse order).")
      super().save(*args, **kwargs)


class ChatMessage(models.Model):
    """
    Represents a single message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    content = models.TextField()  # The message text
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(
        default=False
    )  # Track whether the message has been read
    is_edited = models.BooleanField(default=False) # To track edit.
    edited_at = models.DateTimeField(null=True, blank=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['timestamp']  # Oldest messages first (within a conversation)
        db_table = "ChatMessage"

    def __str__(self):
        return f"From {self.sender.username} to conversation {self.conversation.id} at {self.timestamp}"

    def save(self, *args, **kwargs):
        if self.pk:
            original = ChatMessage.objects.get(pk=self.pk)
            if original.content != self.content:
                self.is_edited = True
                self.edited_at = timezone.now()
        super().save(*args, **kwargs)

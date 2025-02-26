from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Allow login with either username or email
        credentials = {
            'password': attrs.get('password')
        }

        # Check if the input is an email or username
        user_input = attrs.get('username')
        if '@' in user_input:
            credentials['email'] = user_input
        else:
            credentials['username'] = user_input

        # Authenticate the user
        user = self.authenticate_user(credentials)
        if user:
            # Generate the token with custom claims
            data = {}
            refresh = self.get_token(user)
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            return data
        else:
            raise ValidationError('Unable to log in with provided credentials.')

    def authenticate_user(self, credentials):
        # Try to authenticate with username or email
        try:
            if 'email' in credentials:
                user = User.objects.get(email=credentials['email'])
            else:
                user = User.objects.get(username=credentials['username'])
            
            if user.check_password(credentials['password']):
                return user
        except User.DoesNotExist:
            pass
        return None

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = str(user.user_id)  # Convert UUID to string
        return token

# Added the above class bcz we changed the pk of our usr model to user_id, but the default token serializer uses id as the pk
# So we need to override the default token serializer to use user_id instead of id
# we now mentioned this class in the settings.py file
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is write-only
        }

    def create(self, validated_data):
        # Hash the password before saving the user
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

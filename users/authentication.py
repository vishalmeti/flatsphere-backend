from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']  # Use user_id from the token payload
            user = self.user_model.objects.get(user_id=user_id)
        except self.user_model.DoesNotExist:
            raise InvalidToken('User not found')
        return user
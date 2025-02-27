from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            id = validated_token["id"]  # Use id from the token payload
            user = self.user_model.objects.get(id=id)
        except self.user_model.DoesNotExist:
            raise InvalidToken('User not found')
        return user

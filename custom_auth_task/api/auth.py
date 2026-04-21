from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .jwt import decode_jwt
from .models import User


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """Аутентифицирует пользователя по JWT-токену."""
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '):
            return None
        token = auth.split()[1]
        payload = decode_jwt(token)
        if not payload:
            raise AuthenticationFailed('Invalid token')
        try:
            user = User.objects.get(
                id=payload['user_id'],
                is_active=True
            )
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        return (user, None)

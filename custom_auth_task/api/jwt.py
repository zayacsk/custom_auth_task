import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from api.models import User, BlacklistedToken


def generate_jwt(user):
    """Создаёт JWT-токен для активного пользователя."""
    payload = {
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + timedelta(
            seconds=settings.JWT_EXPIRE_SECONDS
        ),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_jwt(token):
    """Декодирует JWT-токен, если он валиден и не находится в чёрном списке."""
    if BlacklistedToken.objects.filter(token=token).exists():
        return None
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token):
    """Возвращает активного пользователя, связанного с JWT-токеном."""
    payload = decode_jwt(token)
    if not payload:
        return None
    try:
        return User.objects.get(id=payload['user_id'], is_active=True)
    except User.DoesNotExist:
        return None

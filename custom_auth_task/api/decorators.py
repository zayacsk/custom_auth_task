from django.contrib.auth.models import AnonymousUser
from rest_framework.response import Response
from .access_policy import AccessPolicy


def access_required(roles=None, permission=None, allow_owner=False):
    """Ограничивает доступ к view по ролям, разрешениям или владению."""
    def decorator(func):
        """Оборачивает view-функцию проверкой прав доступа."""
        def wrapper(self, request, *args, **kwargs):
            """Проверяет доступ и вызывает исходный обработчик при успехе."""
            user = request.user
            if not user or isinstance(user, AnonymousUser):
                return Response({'error': 'Unauthorized'}, status=401)
            if allow_owner:
                if kwargs.get('user_id') and user.id == int(kwargs['user_id']):
                    return func(self, request, *args, **kwargs)
            if permission:
                action, resource = permission
                if not AccessPolicy.can_access(
                    user,
                    action,
                    resource,
                    roles
                ):
                    return Response({'error': 'Forbidden'}, status=403)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator

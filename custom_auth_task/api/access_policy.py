from .permissions import PermissionService


class AccessPolicy:

    @staticmethod
    def can_access(user, action, resource, roles=None):
        """Проверяет доступ пользователя по роли."""
        if roles and PermissionService.has_role(user, roles):
            return True
        return PermissionService.has_permission(user, action, resource)

from api.models import Permission, UserRole


class PermissionService:

    @staticmethod
    def get_user_roles(user):
        """Возвращает queryset ролей, назначенных пользователю."""
        return UserRole.objects.filter(user=user).select_related('role')

    @staticmethod
    def has_role(user, roles: list[str]) -> bool:
        """Проверяет, наличие роли у пользователя."""
        return UserRole.objects.filter(
            user=user,
            role__name__in=roles
        ).exists()

    @staticmethod
    def has_permission(user, action: str, resource: str) -> bool:
        """Проверяет наличие у пользователя разрешения на действие."""
        return Permission.objects.filter(
            action=action,
            resource__name=resource,
            rolepermission__role__userrole__user=user
        ).exists()

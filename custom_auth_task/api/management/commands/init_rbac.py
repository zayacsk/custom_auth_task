import os

from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import (
    User, Role, Resource, Permission,
    RolePermission, UserRole
)

load_dotenv()


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Инициализирует базовые RBAC-сущности, роли и администратора."""
        with transaction.atomic():
            resources_data = [
                {'name': 'users', 'description': 'User management'},
                {'name': 'roles', 'description': 'Role management'},
                {'name': 'resources', 'description': 'Resource management'},
                {'name': 'permissions',
                 'description': 'Permission management'},
                {'name': 'project', 'description': 'Project management'},
            ]
            resources = {}
            for res_data in resources_data:
                resource, _ = Resource.objects.get_or_create(
                    name=res_data['name'],
                    defaults={'description': res_data['description']}
                )
                resources[res_data['name']] = resource
            actions = ['create', 'read', 'update', 'delete']
            permissions = {}
            for resource_name, resource_obj in resources.items():
                for action in actions:
                    perm, _ = Permission.objects.get_or_create(
                        action=action,
                        resource=resource_obj
                    )
                    permissions[f'{action}:{resource_name}'] = perm
            admin_role, _ = Role.objects.get_or_create(
                name='admin',
                defaults={'description': 'Administrator with full access'}
            )
            user_role, _ = Role.objects.get_or_create(
                name='user',
                defaults={'description': 'Default user role'}
            )
            for perm in permissions.values():
                RolePermission.objects.get_or_create(
                    role=admin_role,
                    permission=perm
                )
            RolePermission.objects.get_or_create(
                role=user_role,
                permission=permissions['read:project']
            )
            user, created = User.objects.get_or_create(
                email=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
                defaults={
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_active': True
                }
            )
            user.set_password(os.getenv('ADMIN_PASSWORD', 'admin123'))
            user.save()
            UserRole.objects.get_or_create(
                user=user,
                role=admin_role
            )
        self.stdout.write(self.style.SUCCESS('RBAC initialization completed.'))

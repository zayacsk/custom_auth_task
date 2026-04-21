from rest_framework import serializers
from .models import Project, User, UserRole, Role, Resource, Permission


class UserReadSerializer(serializers.ModelSerializer):
    """Для отображения публичной информации о пользователе."""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active')


class RoleSerializer(serializers.ModelSerializer):
    """Для управления ролями пользователей."""
    class Meta:
        model = Role
        fields = ('id', 'name', 'description')


class ResourceSerializer(serializers.ModelSerializer):
    """Для описания ресурсов."""
    class Meta:
        model = Resource
        fields = ('id', 'name', 'description')


class PermissionSerializer(serializers.ModelSerializer):
    """Для отображения прав."""
    resource = ResourceSerializer()

    class Meta:
        model = Permission
        fields = ('id', 'action', 'resource')


class RegisterSerializer(serializers.ModelSerializer):
    """Для регистрации новых пользователей."""
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password',
            'password_repeat'
        )

    def validate(self, data):
        """Проверяет совпадение пароля и его подтверждения."""
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError('Passwords do not match')
        return data

    def create(self, validated_data):
        """Создаёт пользователя, задаёт пароль и назначает базовую роль."""
        validated_data.pop('password_repeat')
        user = User(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        role = Role.objects.get(name='user')
        UserRole.objects.create(user=user, role=role)
        return user


class LoginSerializer(serializers.Serializer):
    """Для валидации входных данных при аутентификации."""
    email = serializers.EmailField()
    password = serializers.CharField()


class ProjectSerializer(serializers.ModelSerializer):
    """Для создания и отображения данных о проектах."""
    class Meta:
        model = Project
        fields = ('id', 'name', 'description')

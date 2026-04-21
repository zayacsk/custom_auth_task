from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Permission,
    Project,
    Resource,
    Role,
    RolePermission,
    User,
    BlacklistedToken,
    UserRole
)

from .serializers import (
    ProjectSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserReadSerializer,
    RoleSerializer,
    ResourceSerializer,
    PermissionSerializer
)

from .jwt import generate_jwt
from .decorators import access_required


class RegisterView(APIView):

    def post(self, request):
        """Регистрирует нового пользователя и возвращает его данные."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'User created',
            'user': UserReadSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):

    def post(self, request):
        """Аутентифицирует пользователя и возвращает JWT-токен."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User.objects.filter(is_active=True),
            email=serializer.validated_data['email']
        )
        if not user.check_password(serializer.validated_data['password']):
            return Response({'error': 'Invalid credentials'}, status=401)
        token = generate_jwt(user)
        return Response({
            'token': token,
            'user': UserReadSerializer(user).data
        })


class LogoutView(APIView):

    @access_required()
    def post(self, request):
        """Добавляет текущий JWT-токен пользователя в чёрный список."""
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '):
            return Response({'error': 'Invalid token'}, status=400)
        token = auth.split()[1]
        BlacklistedToken.objects.get_or_create(token=token)
        return Response({'message': 'Logged out'})


class UserListView(APIView):

    @access_required(permission=('read', 'users'))
    def get(self, request):
        """Возвращает список активных пользователей."""
        users = (
            User.objects
            .filter(is_active=True)
            .prefetch_related('userrole_set__role')
        )
        return Response(UserReadSerializer(users, many=True).data)


class UserDetailView(APIView):

    @access_required(permission=('read', 'users'), allow_owner=True)
    def get(self, request, user_id):
        """Возвращает данные конкретного активного пользователя."""
        user = (
            User.objects
            .prefetch_related('userrole_set__role')
            .get(id=user_id, is_active=True)
        )
        return Response(UserReadSerializer(user).data)

    @access_required(permission=('update', 'users'), allow_owner=True)
    def put(self, request, user_id):
        """Обновляет профиль пользователя и при необходимости его пароль."""
        user = get_object_or_404(User, id=user_id, is_active=True)
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        if 'password' in request.data:
            user.set_password(request.data['password'])
        user.save()
        return Response({
            'message': 'User updated',
            'user': UserReadSerializer(user).data
        })

    @access_required(permission=('delete', 'users'), allow_owner=True)
    def delete(self, request, user_id):
        """Деактивирует пользователя без физического удаления записи."""
        user = get_object_or_404(User, id=user_id, is_active=True)
        user.is_active = False
        user.save()
        return Response({
            'message': 'User deactivated',
            'user': UserReadSerializer(user).data
        })


class RoleListCreateView(APIView):

    @access_required(roles=['admin'])
    def get(self, request):
        """Возвращает список ролей."""
        roles = (
            Role.objects
            .prefetch_related(
                'rolepermission_set__permission__resource'
            )
        )
        return Response(RoleSerializer(roles, many=True).data)

    @access_required(roles=['admin'])
    def post(self, request):
        """Создаёт новую роль."""
        role = Role.objects.create(
            name=request.data['name'],
            description=request.data.get('description', '')
        )
        return Response({
            'message': 'Role created',
            'role': RoleSerializer(role).data
        }, status=201)


class RoleDetailView(APIView):

    @access_required(roles=['admin'])
    def put(self, request, role_id):
        """Обновляет существующую роль."""
        role = (
            Role.objects
            .prefetch_related(
                'rolepermission_set__permission__resource'
            )
            .get(id=role_id)
        )
        role.name = request.data.get('name', role.name)
        role.description = request.data.get('description', role.description)
        role.save()
        return Response({
            'message': 'Role updated',
            'role': RoleSerializer(role).data
        })

    @access_required(roles=['admin'])
    def delete(self, request, role_id):
        """Удаляет роль по идентификатору."""
        role = get_object_or_404(Role, id=role_id)
        role.delete()
        return Response({'message': 'Role deleted'})


class ResourceListCreateView(APIView):

    @access_required(roles=['admin'])
    def get(self, request):
        """Возвращает список ресурсов."""
        resources = (
            Resource.objects
            .prefetch_related('permission_set')
        )
        return Response(ResourceSerializer(resources, many=True).data)

    @access_required(roles=['admin'])
    def post(self, request):
        """Создаёт новый ресурс."""
        resource = Resource.objects.create(
            name=request.data['name'],
            description=request.data.get('description', '')
        )
        return Response({
            'message': 'Resource created',
            'resource': ResourceSerializer(resource).data
        }, status=201)


class ResourceDetailView(APIView):

    @access_required(roles=['admin'])
    def put(self, request, resource_id):
        """Обновляет существующий ресурс."""
        resource = get_object_or_404(Resource, id=resource_id)
        resource.name = request.data.get('name', resource.name)
        resource.description = request.data.get(
            'description', resource.description)
        resource.save()
        return Response({
            'message': 'Resource updated',
            'resource': ResourceSerializer(resource).data
        })

    @access_required(roles=['admin'])
    def delete(self, request, resource_id):
        """Удаляет ресурс по идентификатору."""
        resource = get_object_or_404(Resource, id=resource_id)
        resource.delete()
        return Response({'message': 'Resource deleted'})


class PermissionCreateView(APIView):

    @access_required(roles=['admin'])
    def post(self, request):
        """Создаёт новое разрешение для указанного ресурса."""
        permission = Permission.objects.create(
            action=request.data['action'],
            resource_id=request.data['resource_id']
        )
        permission = (
            Permission.objects
            .select_related('resource')
            .get(id=permission.id)
        )
        return Response({
            'message': 'Permission created',
            'permission': PermissionSerializer(permission).data
        }, status=201)


class PermissionDeleteView(APIView):

    @access_required(roles=['admin'])
    def delete(self, request, permission_id):
        """Удаляет разрешение по идентификатору."""
        permission = get_object_or_404(Permission, id=permission_id)
        permission.delete()
        return Response({'message': 'Permission deleted'})


class AssignPermissionToRoleView(APIView):

    @access_required(roles=['admin'])
    def post(self, request):
        """Назначает разрешение выбранной роли."""
        rp, _ = RolePermission.objects.get_or_create(
            role_id=request.data['role_id'],
            permission_id=request.data['permission_id']
        )
        return Response({
            'message': 'Permission assigned',
            'role_id': rp.role_id,
            'permission_id': rp.permission_id
        })


class RemovePermissionFromRoleView(APIView):

    @access_required(roles=['admin'])
    def delete(self, request):
        """Удаляет связь между ролью и разрешением."""
        RolePermission.objects.filter(
            role_id=request.data['role_id'],
            permission_id=request.data['permission_id']
        ).delete()
        return Response({'message': 'Permission removed'})


class AssignRoleToUserView(APIView):

    @access_required(roles=['admin'])
    def post(self, request):
        """Назначает роль пользователю."""
        ur, _ = UserRole.objects.get_or_create(
            user_id=request.data['user_id'],
            role_id=request.data['role_id']
        )
        return Response({
            'message': 'Role assigned',
            'user_id': ur.user_id,
            'role_id': ur.role_id
        })


class RemoveRoleFromUserView(APIView):

    @access_required(roles=['admin'])
    def delete(self, request):
        """Удаляет назначенную пользователю роль."""
        UserRole.objects.filter(
            user_id=request.data['user_id'],
            role_id=request.data['role_id']
        ).delete()
        return Response({'message': 'Role removed'})


class ProjectListCreateView(APIView):

    @access_required(permission=('read', 'project'))
    def get(self, request):
        """Возвращает список проектов."""
        projects = Project.objects.all().order_by('-id')
        return Response(ProjectSerializer(projects, many=True).data)

    @access_required(permission=('create', 'project'))
    def post(self, request):
        """Создаёт новый проект."""
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_201_CREATED
        )


class ProjectDetailView(APIView):

    @access_required(permission=('read', 'project'))
    def get(self, request, project_id):
        """Возвращает данные проекта по идентификатору."""
        project = get_object_or_404(Project, id=project_id)
        return Response(ProjectSerializer(project).data)

    @access_required(permission=('update', 'project'))
    def put(self, request, project_id):
        """Частично обновляет проект."""
        project = get_object_or_404(Project, id=project_id)
        serializer = ProjectSerializer(
            project,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @access_required(permission=('delete', 'project'))
    def delete(self, request, project_id):
        """Удаляет проект по идентификатору."""
        project = get_object_or_404(Project, id=project_id)
        project.delete()
        return Response({'message': 'Project deleted'})

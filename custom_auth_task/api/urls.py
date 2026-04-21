from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('users/', views.UserListView.as_view()),
    path('users/<int:user_id>/', views.UserDetailView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('admin/roles/', views.RoleListCreateView.as_view()),
    path('admin/roles/<int:role_id>/', views.RoleDetailView.as_view()),
    path('admin/resources/', views.ResourceListCreateView.as_view()),
    path('admin/resources/<int:resource_id>/',
         views.ResourceDetailView.as_view()),
    path('admin/permissions/', views.PermissionCreateView.as_view()),
    path('admin/permissions/<int:permission_id>/',
         views.PermissionDeleteView.as_view()),
    path('admin/roles/assign-permission/',
         views.AssignPermissionToRoleView.as_view()),
    path('admin/roles/remove-permission/',
         views.RemovePermissionFromRoleView.as_view()),
    path('admin/users/assign-role/', views.AssignRoleToUserView.as_view()),
    path('admin/users/remove-role/', views.RemoveRoleFromUserView.as_view()),
    path('projects/', views.ProjectListCreateView.as_view()),
    path('projects/<int:project_id>/', views.ProjectDetailView.as_view()),
]

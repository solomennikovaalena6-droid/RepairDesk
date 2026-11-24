from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Разрешение: доступ только для пользователей с ролью 'admin'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Admin: full quyền
    User: chỉ xem + tìm kiếm
    """

    def has_permission(self, request, view):
        # GET (xem) → ai cũng được
        if request.method in SAFE_METHODS:
            return True

        # POST, PUT, DELETE → chỉ admin
        return request.user and request.user.is_staff
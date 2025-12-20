from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """
    Allows access only to users with the 'super_admin' user_type.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type_nn == "super_admin"
        )


class IsAdmin(BasePermission):
    """
    Allows access only to users with the 'admin' user_type.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type_nn == "admin"
        )


class IsAccountant(BasePermission):
    """
    Allows access only to users with the 'accountant' user_type.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type_nn == "accountant"
        )


class IsTelecaller(BasePermission):
    """
    Allows access only to users with the 'telecaller' user_type.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type_nn == "telecaller"
        )


class IsSalesman(BasePermission):
    """
    Allows access only to users with the 'salesman' user_type.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type_nn == "salesman"
        )


class IsSupervisor(BasePermission):
    """
    Allows access only users with the 'supervisor' user_type.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type_nn == "supervisor"
        )

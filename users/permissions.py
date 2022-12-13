from rest_framework.permissions import BasePermission


class IsProjectBelongToUser(BasePermission):
    """
    Allows access to project only when it's belongs to user.
    """

    def has_permission(self, request, view):
        project_id = view.kwargs['project_id']
        return request.user.projects.filter(id=project_id).exists()

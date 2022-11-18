from uuid import UUID

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from users.models import Project


def get_api_key_from_header(request_header):
    return request_header.get(settings.API_KEY_HEADER_PARAM_NAME)


def is_valid_uuid(_uuid):
    try:
        UUID(_uuid)
    except ValueError:
        return False
    else:
        return True


def is_valid_api_key(api_key):
    return len(api_key) == settings.API_KEY_LENGTH


class SDKAuthentication(BaseAuthentication):
    def authenticate(self, request, **kwargs):
        api_key = get_api_key_from_header(request.headers)
        if not api_key:
            msg = _('Header is missing!')
            raise AuthenticationFailed(msg)

        if not is_valid_api_key(api_key):
            msg = _('Invalid header!')
            raise AuthenticationFailed(msg)

        project = Project.get_project_object_by_api_key(api_key)
        if not project:
            msg = _('Wrong header parameter!')
            raise AuthenticationFailed(msg)

        return project.user, project

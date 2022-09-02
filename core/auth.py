from uuid import UUID

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import APIKey, Project


def get_api_key_from_header(request_header):
    return request_header.get(settings.API_KEY_HEADER_PARAM_NAME)


def get_project_uuid_from_header(request_header):
    return request_header.get(settings.PROJECT_UUID_HEADER_PARAM_NAME)


def is_valid_uuid(_uuid):
    try:
        UUID(_uuid)
    except ValueError:
        return False
    else:
        return True


def is_valid_api_key(api_key):
    return len(api_key) == settings.API_KEY_LENGTH


class LoggerAuthentication(BaseAuthentication):
    def authenticate(self, request, **kwargs):
        api_key = get_api_key_from_header(request.headers)
        project_uuid = get_project_uuid_from_header(request.headers)
        if not api_key or not project_uuid:
            msg = _('Headers are missing!')
            raise AuthenticationFailed(msg)

        if not is_valid_uuid(project_uuid) or not is_valid_api_key(api_key):
            msg = _('Invalid headers!')
            raise AuthenticationFailed(msg)

        user = APIKey.get_user_object(api_key)
        project = Project.get_project_object(project_uuid)
        if not user or not project:
            msg = _('Wrong header parameters!')
            raise AuthenticationFailed(msg)

        return user, project

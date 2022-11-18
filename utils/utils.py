import secrets

from django.conf import settings


def generate_api_key():
    return secrets.token_hex(settings.API_KEY_LENGTH // 2)

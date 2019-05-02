import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework_jwt.settings import api_settings


expire_delta = api_settings.JWT_REFRESH_EXPIRATION_DELTA

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': user.email,
        'expires': timezone.now() + \
            expire_delta - datetime.timedelta(seconds=200)
    }

def jwt_get_username_from_payload_handler(payload):
    """
    Override this function if username is formatted differently in payload
    """
    return payload.get('user')

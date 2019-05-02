from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_jwt.settings import api_settings

from user.serializer import UserSerializer, AuthTokenSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


User = get_user_model()


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    # authentication_classes = []
    # permission_classes = []

    serializer_class = UserSerializer


class CreateTokenView(APIView):
    """Create new token for user"""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    # def post(self, request, *args, **kwargs):
    #     """Allow username or email as user field"""
    #     if request.user.is_authenticated():
    #         return Response({'detail': 'You are already authenticated.'},
    #                         status=400)
    #     data = request.data
    #     email = data.get('email')
    #     password = data.get('password')
    #     # query for name 
    #     qs = User.objects.filter(
    #         Q(username__iexact=username) |
    #         Q(email__iexact=username)
    #     ).distinct()
    #     if qs.count() == 1:
    #         user_obj = qs.first()
    #         if user_obj.check_password(password):
    #             user = user_obj
    #             payload = jwt_payload_handler(user)
    #             token = jwt_encode_handler(payload)
    #             response = jwt_response_payload_handler(token, user,
    #                                                     request=request)
    #             return Response(response)
    #     return Response({'detail': 'Invalid credentials'}, status=401)

    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        payload = jwt_payload_handler(request.user)
        token = jwt_encode_handler(payload)
        response = jwt_response_payload_handler(token, request.user,
                                                request=request)
        return Response(response)
    

class RefreshTokenView(RefreshJSONWebToken):
    pass

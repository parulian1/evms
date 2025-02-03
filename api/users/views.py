from http import HTTPStatus

from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from api.users.serializers import RegistrationSerializer, CustomTokenObtainPairSerializer, UserSerializer


# Create your views here.
class RegistrationView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer


class CustomObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(APIView):
    serializer_class = UserSerializer
    def get(self, request):
        user = request.user
        if not user:
            return Response(status=HTTPStatus.UNAUTHORIZED)
        serializer = UserSerializer(user)

        return Response(serializer.data)
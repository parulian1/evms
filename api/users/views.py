from http import HTTPStatus

from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from drf_yasg.utils import swagger_auto_schema

from api.users.serializers import RegistrationSerializer, CustomTokenObtainPairSerializer, UserSerializer, \
    TokenObtainPairResponseSerializer
from api.utils.serializers import UnauthorizedSerializer


# Create your views here.
class RegistrationView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer


class CustomObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        }
    )
    def post(self, request: Request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_401_UNAUTHORIZED: UnauthorizedSerializer
        }
    )
    def get(self, request):
        user = request.user
        if not user.id :
            return Response(status=HTTPStatus.UNAUTHORIZED)
        serializer = UserSerializer(user)

        return Response(serializer.data)
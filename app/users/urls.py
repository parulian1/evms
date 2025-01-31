from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.users.views import RegistrationView, CustomObtainTokenPairView, UserProfileView

app_name = 'users'

urlpatterns = [
    path('login/', CustomObtainTokenPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]

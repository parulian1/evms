from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from api.users.views import RegistrationView, CustomObtainTokenPairView, UserProfileView

app_name = 'users'

urlpatterns = [
    path('', include('api.users.urls', namespace='user-attendee')),
    path('', include('api.track.urls', namespace='track')),
    # path('', include('api.session_management.urls', namespace='session-management')),
]

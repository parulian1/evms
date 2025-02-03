import openapi
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework_nested.routers import NestedDefaultRouter

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from api.session_management.views import EventViewSet, SessionViewSet, SessionPurchaseViewSet
from api.track.views import VenueViewSet, TrackViewSet
from api.users.views import CustomObtainTokenPairView, RegistrationView, UserProfileView

app_name = 'api'

router = DefaultRouter()
router.register(r'venue', VenueViewSet, basename='venue')
router.register(r'track', TrackViewSet, basename='track')

router.register(r'event', EventViewSet, basename='event')
router.register(r'session', SessionViewSet, basename='session')

session_router = NestedDefaultRouter(router, 'session', lookup='session')
session_router.register(r'purchase', SessionPurchaseViewSet, basename='session-purchase')

schema_view = get_schema_view(
    openapi.Info(
        title="Event Management System API",
        default_version='v1',
        description="""Event Management System API will handle technical conferences, managing everything from event creation to attendee
registration and session scheduling.""",
        contact=openapi.Contact(email="martogi.parulian86@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(session_router.urls)),
    path('users/', include([
        path('login/', CustomObtainTokenPairView.as_view(), name='login'),
        path('refresh/', TokenRefreshView.as_view(), name='refresh-token'),
        path('register/', RegistrationView.as_view(), name='register'),
        path('profile/', UserProfileView.as_view(), name='profile'),
    ]), name='users'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # # Optional UI:
    # path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

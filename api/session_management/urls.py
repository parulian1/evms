from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.session_management.views import EventViewSet

app_name = 'session_management'
router = DefaultRouter()
# router.register(r'session', 'session', basename='session')
router.register(r'event', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
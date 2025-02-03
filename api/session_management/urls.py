from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.session_management.views import EventViewSet, SessionViewSet

app_name = 'session_management'
router = DefaultRouter()
router.register(r'event', EventViewSet, basename='event')
router.register(r'session', SessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]
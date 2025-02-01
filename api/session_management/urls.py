from django.urls import include, path
from rest_framework.routers import DefaultRouter


app_name = 'session_management'
router = DefaultRouter()
router.register(r'session', 'session', basename='session')
router.register(r'event', 'event', basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
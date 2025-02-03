from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from api.session_management.views import EventViewSet, SessionViewSet

app_name = 'session_management'
router = DefaultRouter()
router.register(r'event', EventViewSet, basename='event')
router.register(r'session', SessionViewSet, basename='session')

session_purchase_router = NestedDefaultRouter(router, 'session', lookup='session')
session_purchase_router.register(r'purchase', SessionViewSet, basename='session-purchase')


urlpatterns = [
    path('', include(router.urls)),
]
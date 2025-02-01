from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import track
from api.track.views import VenueViewSet, TrackViewSet

app_name = 'track'

router = DefaultRouter()
router.register(r'venue', VenueViewSet, basename='venue')
router.register(r'track', TrackViewSet, basename='track')

urlpatterns = [
    path('', include(router.urls)),
    # path('track', None, name='track'),
]
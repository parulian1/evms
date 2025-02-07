from rest_framework.viewsets import ModelViewSet

from api.track.models import Venue, Track
from api.track.serializers import VenueSerializer, TrackSerializer
from api.utils.permissions import IsStaffOrAdmin, IsReadOnly


# Create your views here.
class VenueViewSet(ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]
    lookup_field = 'id'


class TrackViewSet(ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]
    lookup_field = 'id'

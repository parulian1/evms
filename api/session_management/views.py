from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from api.session_management.models import Event
from api.session_management.serializers import EventSerializer
from api.utils.permissions import IsStaffOrAdmin, IsReadOnly


# Create your views here.
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]

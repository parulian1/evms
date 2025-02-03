from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from api.session_management.models import Event, Session
from api.session_management.serializers import EventSerializer, SessionSerializer, CreateAndUpdateSessionSerializer
from api.utils.permissions import IsStaffOrAdmin, IsReadOnly


# Create your views here.
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]


class SessionViewSet(ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CreateAndUpdateSessionSerializer
        return self.serializer_class
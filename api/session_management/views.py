from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins

from api.session_management.models import Event, Session
from api.session_management.serializers import EventSerializer, SessionSerializer, CreateAndUpdateSessionSerializer, \
    CreateAndUpdateEventSerializer
from api.utils.permissions import IsStaffOrAdmin, IsReadOnly


# Create your views here.
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CreateAndUpdateEventSerializer
        return self.serializer_class


class SessionViewSet(ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CreateAndUpdateSessionSerializer
        return self.serializer_class


class SessionPurchaseViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = SessionSerializer

    def get_session(self):
        try:
            return Session.objects.get(
                id=self.kwargs.get('id')
            )
        except Session.DoesNotExist:
            raise Http404()

    def create(self, request, *args, **kwargs):
        instance = self.get_session()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


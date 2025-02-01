from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from api.session_management.models import Event


# Create your views here.
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()

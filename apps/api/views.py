from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.response import Response

from django.contrib.auth.models import User

from core.models import *
from core.serializers import *


class Events(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class Persons(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class Users(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class Pages(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer



from django.shortcuts import render
from django.http import Http404, HttpResponseNotFound
from rest_framework import viewsets, generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.decorators import api_view

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
    queryset = Page.objects.order_by("weight")
    serializer_class = PageSerializer


@api_view(('GET',))
def page_slug(request, slug):
    """
    Courses ids.
    """

    try:
        page = Page.objects.get(slug=slug)
    except:
        page = None

    if not page:
        try:
            page = Page.objects.get(pk=slug)
        except:
            page = None

    if page:
        return Response({
            "id": page.id,
            "slug": page.slug,
            "title": page.title,
            "html": page.html,
            "pages": page.get_pages_dict(),
            "keywords": page.keywords,
            "type": Type.objects.get(pk=page.type).values("title"),

        })
    else:
        raise Http404



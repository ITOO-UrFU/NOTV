from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.contrib.auth.models import User

from core.models import *
from core.serializers import *


class Events(viewsets.ModelViewSet):
    queryset = Event.objects.filter(status="p")
    serializer_class = EventSerializer


class Persons(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by("karma")
    serializer_class = PersonSerializer


class Users(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class Pages(viewsets.ModelViewSet):
    queryset = Page.objects.filter(status="p").order_by("weight")
    serializer_class = PageSerializer


class Paths(viewsets.ModelViewSet):
    queryset = Path.objects.all()
    serializer_class = PathSerializer



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

    try:
        type = Type.objects.filter(pk=page.type.id).values("title").first()["title"]
    except:
        type = None

    if page:
        return Response({
            "id": page.id,
            "slug": page.slug,
            "title": page.title,
            "html": page.html,
            "pages": page.get_pages_dict(),
            "keywords": page.keywords,
            "type": type,
            "weight": page.weight,

        })
    else:
        raise Http404



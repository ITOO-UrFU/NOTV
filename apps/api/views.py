from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.utils.translation import ugettext_lazy as _

import jwt
from django.conf import settings

from django.contrib.auth.models import User

from core.models import *
from core.serializers import *


class Events(viewsets.ModelViewSet):
    queryset = Event.objects.filter(status="p")
    serializer_class = EventSerializer


class Speakers(viewsets.ModelViewSet):
    serializer_class = SpeakerSerializer

    def get_queryset(self):
        type = RegistrationType.objects.filter(title="Спикер").first()
        speakers = Person.objects.filter(id__in=EventUserRegistration.objects.filter(type=type).values('person_id')).order_by("-karma")
        return speakers


class Persons(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by("-karma")
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
@permission_classes((permissions.AllowAny,))
def page_slug(request, slug):
    """
    Courses ids.
    """

    page = get_page_by_pk_or_slug(slug)

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


def get_page_by_pk_or_slug(slug):
    try:
        page = Page.objects.get(slug=slug)
    except:
        page = None
    if not page:
        try:
            page = Page.objects.get(pk=slug)
        except:
            page = None
    return page


class UserViewSet(viewsets.ModelViewSet):
    def create(self, request, format=None):
        user = User.objects.create(
            url=request['url'],
            email=request['email'],
        )
        return user


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status="201")
        return Response(serializer.errors, status="400")

    def list(self, request):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response()


class PersonDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = PersonSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):

        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object(request)
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)

    def get_object(self, request):
        return self.get_or_update_person_by_jwt()

    def get_or_update_person_by_jwt(self):
        jwt_token = self.request.META.get('HTTP_AUTHORIZATION', None)
        if jwt_token:
            token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            current_user = User.objects.get(pk=token_data['user_id'])

            try:
                person = Person.objects.get(user=current_user)
            except:
                person = Person(user=current_user)
                person.save()

            return person

        else:
            return None

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        https://github.com/Tivix/django-rest-auth/issues/275
        """

        return Person.objects.get(user=self.request.user)


class PersonUpdate(generics.UpdateAPIView):
    serializer_class = PersonSerializerSimple
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object(request)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_object(self, request):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        return self.get_or_update_person_by_jwt()

    def get_or_update_person_by_jwt(self):
        jwt_token = self.request.META.get('HTTP_AUTHORIZATION', None)
        if jwt_token:
            token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            current_user = User.objects.get(pk=token_data['user_id'])

            try:
                person = Person.objects.get(user=current_user)
            except:
                person = Person(user=current_user)
                person.save()

            return person

        else:
            return None

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        https://github.com/Tivix/django-rest-auth/issues/275
        """

        return None


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def register_on_event(request):
    #
    # try:

    jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
    # if jwt_token:
    token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
    current_user = User.objects.get(pk=token_data['user_id'])
    person = Person(user=current_user)
    print('!!!!!!!!!!!!!!!!!!!!!!!!', request.POST.get('event_id'))
    event = Event.objects.get(id=request.POST.get('event_id'))
    type = RegistrationType.objects.filter(title="Участник").first()

    eur = EventUserRegistration(person=person, event=event, status="r", type=type)
    eur.save()

    return Response({"success": True})
    # else:
    #         return Response({"success": False})

    # except:
    #
    #     return Response({"success": False})

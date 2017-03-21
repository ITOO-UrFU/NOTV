from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import permissions
from django.db.models import Q

from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.utils.translation import ugettext_lazy as _

import jwt
from django.conf import settings

from django.contrib.auth.models import User

from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_auth.models import TokenModel
from rest_auth.registration.app_settings import RegisterSerializer
from allauth.account import app_settings as allauth_settings
from rest_auth.app_settings import (TokenSerializer,
                                    JWTSerializer,
                                    create_token)
from allauth.account.utils import complete_signup
from rest_auth.utils import jwt_encode
from importlib import import_module
from six import string_types

from core.models import *
from core.serializers import *


class Events(viewsets.ModelViewSet):
    queryset = Event.objects.filter(status="p")
    serializer_class = EventSerializer


class Speakers(viewsets.ModelViewSet):
    serializer_class = SpeakerSerializer

    def get_queryset(self):
        type = RegistrationType.objects.filter(title="Спикер").first()
        speakers = Person.objects.filter(Q(id__in=EventUserRegistration.objects.filter(type=type).values('person_id')) | Q(user=None))

        return speakers.order_by("-karma")


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

    if page:
        try:
            type = Type.objects.filter(pk=page.type.id).values("title").first()["title"]
        except:
            type = None

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
            try:
                token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            except jwt.exceptions.ExpiredSignatureError:
                return Response({"status": "Session expired"})

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
            try:
                token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            except jwt.exceptions.ExpiredSignatureError:
                return Response({"status": "Session expired"})
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

    try:

        jwt_token = request.META.get('HTTP_AUTHORIZATION', None)

        if jwt_token:
            try:
                token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            except jwt.exceptions.ExpiredSignatureError:
                return Response({"status": "Session expired"})
            current_user = User.objects.get(pk=token_data['user_id'])
            person = Person.objects.get(user=current_user)
            event = Event.objects.get(id=request.data.get('event_id'))
            type = RegistrationType.objects.filter(title="Участник").first()

            try:
                eur = EventUserRegistration(person=person, event=event, status="r", type=type)
                eur.save()
            except:
                eur = EventUserRegistration.objects.filter(person=person, event=event)
                if eur:
                    return Response({"success": False})

            return Response({"success": True})

        else:

            return Response({"success": False})
    except:
        return Response({"success": False})


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def unregister_on_event(request):

    try:

        jwt_token = request.META.get('HTTP_AUTHORIZATION', None)

        if jwt_token:
            try:
                token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            except jwt.exceptions.ExpiredSignatureError:
                return Response({"status": "Session expired"})
            current_user = User.objects.get(pk=token_data['user_id'])
            person = Person.objects.get(user=current_user)
            event = Event.objects.get(id=request.data.get('event_id'))
            type = RegistrationType.objects.filter(title="Участник").first()

            try:
                eur = EventUserRegistration.objects.filter(person=person, event=event, type=type)
                if eur:
                    eur.delete()
                    return Response({"success": True})
            except:
                return Response({"success": False})
        else:
            return Response({"success": False})
    except:
        return Response({"success": False})


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def event_user_list(request):

    try:

        jwt_token = request.META.get('HTTP_AUTHORIZATION', None)

        if jwt_token:
            try:
                token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            except jwt.exceptions.ExpiredSignatureError:
                return Response({"status": "Session expired"})
            current_user = User.objects.get(pk=token_data['user_id'])
            person = Person.objects.get(user=current_user)

            try:
                eur = EventUserRegistration.objects.filter(person=person).values("event_id")
                return Response(eur)
            except:
                return Response({"success": False})
        else:
            return Response({"success": False})
    except:
        return Response({"success": False})


def import_callable(path_or_callable):
    if hasattr(path_or_callable, '__call__'):
        return path_or_callable
    else:
        assert isinstance(path_or_callable, string_types)
        package, attr = path_or_callable.rsplit('.', 1)
        return getattr(import_module(package), attr)
    
sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password1', 'password2')
)


def register_permission_classes():
    permission_classes = [AllowAny, ]
    for klass in getattr(settings, 'REST_AUTH_REGISTER_PERMISSION_CLASSES', tuple()):
        permission_classes.append(import_callable(klass))
    return tuple(permission_classes)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = register_permission_classes()
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def get_response_data(self, user):

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': user,
                'token': self.token
            }
            return JWTSerializer(data).data
        else:
            return TokenSerializer(user.auth_token).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(user)
        else:
            create_token(self.token_model, user, serializer)

        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user
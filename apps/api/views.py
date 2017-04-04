from django.http import Http404
from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from django.db.models import Q
from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _

import jwt
from django.conf import settings

from django.contrib.auth.models import User

from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_auth.models import TokenModel
from allauth.account import app_settings as allauth_settings
from rest_auth.app_settings import (TokenSerializer,
                                JWTSerializer,
                                create_token)
from allauth.account.utils import complete_signup
from rest_auth.utils import jwt_encode
from importlib import import_module
from six import string_types

from allauth.account.adapter import get_adapter
from allauth.utils import email_address_exists
from allauth.account.utils import setup_user_email

from rest_framework_extensions.cache.mixins import CacheResponseMixin
from django.views.decorators.cache import cache_page
from core.models import *
from core.serializers import *
from rest_framework import permissions

import os
import hashlib
import uuid


def key():

    key = hashlib.md5(os.urandom(128)).hexdigest()
    return key


def generate_new_filename(filename):
    f, ext = os.path.splitext(filename)
    filename = '%s%s' % (uuid.uuid4().hex, ext)
    fullpath = 'documents/' + filename
    return fullpath


class IsReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow read-only operations.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True


class Events(CacheResponseMixin, viewsets.ModelViewSet):
    permission_classes = (IsReadOnly, )
    queryset = Event.objects.filter(status="p")
    serializer_class = EventSerializer


class Speakers(CacheResponseMixin, viewsets.ModelViewSet):
    serializer_class = SpeakerSerializer

    def get_queryset(self):
        types = RegistrationType.objects.exclude(title="Участник")
        speakers = Person.objects.filter(Q(id__in=EventUserRegistration.objects.filter(type__in=types).values('person_id')) | Q(user=None))

        return speakers.order_by("-karma")


class Persons(CacheResponseMixin, viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by("-karma")
    serializer_class = PersonSerializer


class Users(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class Pages(CacheResponseMixin, viewsets.ModelViewSet):
    queryset = Page.objects.filter(status="p").order_by("weight")
    serializer_class = PageSerializer


class Paths(viewsets.ModelViewSet):
    queryset = Path.objects.all()
    serializer_class = PathSerializer


@api_view(('GET',))
@permission_classes((permissions.AllowAny,))
@cache_page(60 * 5)
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


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=256,
        min_length=3,
        required=False
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    second_name = serializers.CharField()
    position = serializers.CharField()
    organisation = serializers.CharField()
    participation = serializers.CharField()
    phone = serializers.CharField()

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        if data['first_name'] is None or data['last_name'] is None or data['position'] is None or data['organisation'] is None:
            raise serializers.ValidationError(_("Fields can not be empty."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'second_name': self.data.get('second_name', ''),
            'participation': self.data.get('participation', ''),
            'position': self.validated_data.get('position', ''),
            'organisation': self.validated_data.get('organisation', ''),
            'phone': self.validated_data.get('phone', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        person = Person(user=user,
                        first_name=self.cleaned_data['first_name'],
                        last_name=self.cleaned_data['last_name'],
                        second_name=self.cleaned_data['second_name'],
                        organisation=self.cleaned_data['organisation'],
                        position=self.cleaned_data['position'],
                        phone=self.cleaned_data['phone'],
                        participation=self.cleaned_data['participation']
        )

        person.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


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


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def delete_file(request):

    try:
        jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
        if jwt_token:
            try:
                token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            except jwt.exceptions.ExpiredSignatureError:
                return Response({"status": "Session expired"})
            current_user = User.objects.get(pk=token_data['user_id'])
            person = Person.objects.get(user=current_user)
    except:
        pass
    if person:
        file_id = request.data.get("file_id", "")
        print('!!!!!!!!', person.id, file_id)

    if file_id:
        person.docs.delete(Document.objects.get(id=file_id))

    return Response(status=204)


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def file_upload(request):
    try:
        jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
        if jwt_token:
            try:
                token_data = jwt.decode(jwt_token, settings.SECRET_KEY)
            except jwt.exceptions.ExpiredSignatureError:
                return Response({"status": "Session expired"})
            current_user = User.objects.get(pk=token_data['user_id'])
            person = Person.objects.get(user=current_user)
    except:
        return Response(status=403)

    file_obj = request.data["uploadFile"]
    file_addr = generate_new_filename(file_obj.name)

    import io

    with io.open('media/' + file_addr, 'wb+') as f:
        document = Document(title=file_obj.name, file=file_addr)
        document.save()
        for chunk in file_obj.chunks():
            f.write(chunk)
    if document:
        person.docs.add(document)

    return Response({"request": str(request.data)})

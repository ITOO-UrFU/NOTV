from .models import *
from rest_framework import serializers

from django_countries.serializer_fields import CountryField


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "last_login",
            "is_superuser",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
            # "groups",
            # "user_permissions"
        )


class RegistrationTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegistrationType
        fields = ("title", )


class EventSerializer_noperson(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ("id", "title", "description", "get_type_display", "startdate", "enddate")


class EventUserRegistrationSerializer_noperson(serializers.ModelSerializer):
    type = RegistrationTypeSerializer()
    event = EventSerializer_noperson()

    class Meta:
        model = EventUserRegistration
        fields = ("id", "type", "event",  "status")


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    country = CountryField()
    user = UserSerializer()
    get_events = EventUserRegistrationSerializer_noperson(many=True)

    class Meta:
        model = Person
        fields = ("id", "first_name", "last_name", "second_name", "sex", "alt_email", "birthday_date", "organisation", "position", "division", "photo", "biography", "country", "user", "get_events")
        depth = 2


class EventUserRegistrationSerializer(serializers.ModelSerializer):
    person = PersonSerializer()

    class Meta:
        model = EventUserRegistration
        fields = ("id", "person", "get_type_display", "status")


class EventSerializer(serializers.ModelSerializer):
    get_users = EventUserRegistrationSerializer(many=True)

    class Meta:
        model = Event
        fields = ("id", "title", "description", "get_users", "get_type_display", "get_type_display", "startdate", "enddate")


class PageSerializer(serializers.ModelSerializer):
    pages = serializers.SerializerMethodField('get_alternate_name')

    def get_alternate_name(self, obj):
        return obj.get_pages_list()

    class Meta:
        model = Page
        fields = ("id", "slug", "title", "html", "keywords", "pages", "type")


# class PageDetail(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Page

class RegistrationTypeDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegistrationType


class EventUserRegistrationDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventUserRegistration


class EventDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event


class PersonDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person


class UserDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
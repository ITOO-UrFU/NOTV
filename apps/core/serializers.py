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


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    country = CountryField()
    user = UserSerializer()
    class Meta:
        model = Person
        fields = ("id", "first_name", "last_name", "second_name", "sex", "alt_email", "birthday_date", "biography", "country", "user")
        depth = 2


class RegistrationTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegistrationType
        fields = ("title", )

class EventUserRegistrationSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    type = RegistrationTypeSerializer()
    class Meta:
        model = EventUserRegistration
        fields = ("id", "person", "type", "status")


class EventSerializer(serializers.ModelSerializer):
    get_users = EventUserRegistrationSerializer(many=True)
    class Meta:
        model = Event
        fields = ("id", "title", "description", "get_users", "startdate", "enddate")




class PageSerializer(serializers.ModelSerializer):
    pages = serializers.SerializerMethodField('get_alternate_name')

    def get_alternate_name(self, obj):
        return obj.get_pages_list()

    class Meta:
        model = Page
        fields = ("id", "slug", "title", "html", "keywords", "pages")


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
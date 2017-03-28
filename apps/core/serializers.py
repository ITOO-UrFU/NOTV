from .models import *
from rest_framework import serializers

from django_countries.serializer_fields import CountryField
from django.utils import timezone


class DateTimeFieldWihTZ(serializers.DateTimeField):

    def to_representation(self, value):
        # value = timezone.localtime(value)
        return super(DateTimeFieldWihTZ, self).to_representation(value)


class ExtensibleModelSerializer(serializers.ModelSerializer):
    """
    ModelSerializer in which non native extra fields can be specified.
    """

    def restore_object(self, attrs, instance=None):
        """
        Deserialize a dictionary of attributes into an object instance.
        You should override this method to control how deserialized objects
        are instantiated.
        """

        for field in self.opts.non_native_fields:
            attrs.pop(field)

        return super(ExtensibleModelSerializer, self).restore_object(attrs, instance)

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self.fields.items():
            if field_name in self.opts.non_native_fields:
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('title', 'file')


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ('title', 'slug')


class LineOfWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineOfWork
        fields = ('title', 'slug')


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('title', 'slug', 'address', 'housing')


class PathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Path
        fields = ('title', 'slug',)


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class PersonSerializerSimple(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Person
        fields = ("first_name", "last_name", "second_name", "sex", "alt_email", "birthday_date", "organisation", "position", "division", "participation", "photo", "phone", "biography")  # "country",
        depth = 2


class RegistrationTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegistrationType
        fields = ("title", )


class EventUserRegistrationSerializer(serializers.ModelSerializer):
    person = PersonSerializerSimple()

    class Meta:
        model = EventUserRegistration
        fields = ("id", "person", "get_type_display", "status")


class EventSerializer_noperson(serializers.ModelSerializer):
    startdate = DateTimeFieldWihTZ()
    enddate = DateTimeFieldWihTZ()
    get_speakers = EventUserRegistrationSerializer(many=True)

    class Meta:
        model = Event
        fields = ("id", "title", "description", "get_block_slug", "get_speakers", "get_type_display", "get_event_slug", "startdate", "enddate")


class EventUserRegistrationSerializer_noperson(serializers.ModelSerializer):
    type = RegistrationTypeSerializer()
    event = EventSerializer_noperson()

    class Meta:
        model = EventUserRegistration
        fields = ("id", "type", "event",  "status")


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    photo_url = serializers.SerializerMethodField()
    # country = CountryField()
    user = UserSerializer()
    get_events = EventUserRegistrationSerializer_noperson(many=True)
    docs = DocumentSerializer(many=True)

    def get_photo_url(self, person):
        request = self.context.get('request')
        try:
            if person.photo:
                photo_url = person.photo.url
                return request.build_absolute_uri(photo_url)
            else:
                return None
        except:
            return None

    class Meta:
        model = Person
        fields = ("id", "first_name", "last_name", "second_name", "sex", "alt_email", "birthday_date", "organisation", "position", "division", "photo_url", "biography", "participation", "user", "phone", "get_events", "docs")  # "country",
        depth = 1


class SpeakerSerializer(serializers.HyperlinkedModelSerializer):
    # get_events = EventUserRegistrationSerializer_noperson(many=True)
    photo_url = serializers.SerializerMethodField()

    def get_photo_url(self, person):
        request = self.context.get('request')
        try:
            if person.photo:
                photo_url = person.photo.url
                return request.build_absolute_uri(photo_url)
            else:
                return None
        except:
            return None

    class Meta:
        model = Person
        fields = ("first_name", "last_name", "second_name", "sex", "alt_email", "birthday_date", "organisation", "position", "division", "photo_url", "biography")  # "country",
        depth = 1



class EventSerializer(serializers.ModelSerializer):
    get_speakers = EventUserRegistrationSerializer(many=True)
    room = RoomSerializer()
    path = PathSerializer()
    startdate = DateTimeFieldWihTZ()
    enddate = DateTimeFieldWihTZ()

    class Meta:
        model = Event
        fields = ("id", "title", "description", "get_speakers", "get_type_display", "get_block_slug", "get_event_slug", "get_line_of_work_slug", "room", "path", "startdate", "enddate")


class PageSerializer(serializers.ModelSerializer):
    pages = serializers.SerializerMethodField('get_alternate_name')

    def get_alternate_name(self, obj):
        return obj.get_pages_list()

    class Meta:
        model = Page
        fields = ("id", "slug", "title", "html", "keywords", "pages", "type", "weight")


class RegistrationTypeDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegistrationType


class EventUserRegistrationDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventUserRegistration


class LineOfWorkRegistrationDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LineOfWork


class EventDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event


class PersonDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person


class UserDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User


class TypeDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Type


class RoomDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room


class PathDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Path
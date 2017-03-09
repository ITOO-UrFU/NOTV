from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Event)
class EventAdmin(VersionAdmin):
    list_display = ('title', 'description', 'path', 'startdate', 'enddate')
    # fields = ('title', 'description', 'startdate', 'enddate')
    search_fields = ('title', 'description', 'path')
    list_filter = ('startdate', 'enddate', 'path')


@admin.register(CustomObject)
class CustomObjectAdmin(VersionAdmin):
    fields = ("title", "json")
    search_fields = ("title",)


@admin.register(RegistrationType)
class RegistrationTypeAdmin(VersionAdmin):
    fields = ("title",)


@admin.register(EventUserRegistration)
class EventUserRegistrationAdmin(VersionAdmin):
    fields = ("person", "event", "type", "status")
    list_display = ("__str__", "status")
    search_fields = ("__str__",)
    list_filter = ("person", "event", "type", "status")


@admin.register(Page)
class PageAdmin(VersionAdmin):
    fields = ("slug", "weight", "title", "html", "pages", "keywords", "type")
    list_display = ("slug", "title", "weight", "html", "get_pages_display", "keywords", "type")
    filter_horizontal = ('pages',)


@admin.register(Person)
class PersonAdmin(VersionAdmin):
    list_display = ("__str__", "first_name", "last_name", "second_name", "sex", "alt_email", "birthday_date", "biography")


@admin.register(Type)
class TypeAdmin(VersionAdmin):
    fields = ("title", "slug")
    list_display = ("title", "slug")


@admin.register(EventType)
class EventTypeAdmin(VersionAdmin):
    fields = ("title", "slug")
    list_display = ("title", "slug")


@admin.register(Room)
class RoomAdmin(VersionAdmin):
    list_display = ("slug", "title", 'address', 'housing')


@admin.register(Path)
class PathAdmin(VersionAdmin):
    list_display = ("slug", "title")



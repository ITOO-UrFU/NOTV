from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from import_export import resources
from reversion.admin import VersionAdmin
from import_export.admin import ImportExportModelAdmin

from .models import *


class PkResource(resources.ModelResource):
    class Meta:
        model = PK


@admin.register(Event)
class EventAdmin(VersionAdmin):
    list_display = ('title', 'description', 'path', 'block', '_startdate', '_enddate', "line_of_work", "status")
    # fields = ('title', 'description', '_startdate', '_enddate')
    search_fields = ('title', 'description', 'path', "status")
    list_filter = ("_startdate", "_enddate", 'block', 'path', "line_of_work", "status")


@admin.register(CustomObject)
class CustomObjectAdmin(VersionAdmin):
    fields = ("title", "json", "status")
    search_fields = ("title", "status")


@admin.register(RegistrationType)
class RegistrationTypeAdmin(VersionAdmin):
    fields = ("title",)


@admin.register(EventUserRegistration)
class EventUserRegistrationAdmin(AjaxSelectAdmin):
    fields = ("person", "event", "type", "status")
    list_display = ("__str__", "status")
    search_fields = ("__str__",)
    list_filter = ("person", "event", "type", "status")
    # raw_id_fields = ("person", "event")
    form = make_ajax_form(EventUserRegistration, {'person': 'person', 'event': 'event'})


@admin.register(Page)
class PageAdmin(VersionAdmin):
    fields = ("slug", "weight", "title", "html", "title_en", "html_en", "pages", "keywords", "type", "status")
    list_display = ("slug", "title", "weight", "html", "get_pages_display", "keywords", "type", "status")
    filter_horizontal = ('pages',)
    search_fields = ("slug", "title", "weight", "html", "title_en", "html_en", "get_pages_display", "keywords", "type", "status")
    list_filter = ("keywords", "type", "status", "weight", "slug")
    save_as = True


@admin.register(Document)
class DocumentAdmin(VersionAdmin):
    list_display = ("title", "file", 'get_user')
    fields = ("title", "file")


@admin.register(Person)
class PersonAdmin(VersionAdmin):
    list_display = ("__str__", "first_name", "last_name", "second_name", "sex", "alt_email", "birthday_date", "phone", "participation", "get_docs", "institute", "suggestions", "created_at", "user")
    list_filter = ("user",)


@admin.register(Type)
class TypeAdmin(VersionAdmin):
    fields = ("title", "slug")
    list_display = ("title", "slug")


@admin.register(Block)
class BlockAdmin(VersionAdmin):
    fields = ("title", "slug")
    list_display = ("title", "slug")


@admin.register(LineOfWork)
class LineOfWorkAdmin(VersionAdmin):
    fields = ("title", "slug")
    list_display = ("title", "slug")


@admin.register(EventType)
class EventTypeAdmin(VersionAdmin):
    fields = ("title", "title_en", "slug")
    list_display = ("title", "title_en", "slug")


@admin.register(Room)
class RoomAdmin(VersionAdmin):
    list_display = ("slug", "title", 'address', 'housing')


@admin.register(Path)
class PathAdmin(VersionAdmin):
    list_display = ("slug", "title")


@admin.register(PK)
class PKAdmin(VersionAdmin, ImportExportModelAdmin):
    list_display = ("person", "status", "get_pres")


@admin.register(Presentation)
class PresentationAdmin(VersionAdmin):
    resource_class = PkResource
    list_display = ("title", "file", 'get_user')
    fields = ("title", "file")

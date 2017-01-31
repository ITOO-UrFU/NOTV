from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Event)
class EventAdmin(VersionAdmin):
    list_display = ('title', 'description', 'get_speakers', 'startdate', 'enddate')
    fields = ('title', 'description', 'speakers', 'startdate', 'enddate')
    search_fields = ('title', 'descroption', 'speakers')
    list_filter = ('startdate', 'enddate', 'speakers')
    filter_horizontal = ('speakers', )


@admin.register(Speaker)
class SpeakerAdmin(VersionAdmin):
    fields = ("person",)
    search_fields = ("person",)


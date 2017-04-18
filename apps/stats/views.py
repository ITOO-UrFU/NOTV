from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.contrib.admin.views.decorators import staff_member_required

from core.models import *


@staff_member_required
@cache_page(60 * 5)
def events_members(request):
    context = {}
    persons_online = Person.objects.filter(participation='O').count()
    events = Event.objects.all()
    context["events"] = events
    context["persons_online"] = persons_online
    return render(request, 'members.html', context)

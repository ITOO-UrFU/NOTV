from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from core.models import *


@staff_member_required
def events_members(request):
    context = {}
    context["event_members"] = {}
    events = Event.objects.all()
    context["events"] = events
    for event in events:
        members = [x.person for x in EventUserRegistration.objects.filter(event=event)]
        context["event_members"][event.title] = members

    return render(request, 'members.html', context)

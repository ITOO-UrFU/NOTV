from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.contrib.admin.views.decorators import staff_member_required

from core.models import *

from django.contrib.auth.models import User


@staff_member_required
@cache_page(60 * 5)
def events_members(request):
    context = {}
    persons_online = Person.objects.filter(participation='O').count()
    events = Event.objects.all()
    context["events"] = events
    context["persons_online"] = persons_online
    return render(request, 'members.html', context)

@staff_member_required
def all_persons(request):
    context = {}
    persons = Person.objects.all()
    context["persons"] = persons
    eur = EventUserRegistration.objects.all()
    return render(request, 'all.html', context)


def get_all_speakers(request):
    registrations = EventUserRegistration.objects.all().exclude(type__title="Участник")
    return render(request, "speakers.html", {"eurs": registrations})

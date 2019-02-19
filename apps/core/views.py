from ajax_select.fields import AutoCompleteField
from django import forms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from .models import CustomObject


def custom_json_view(request, title):
    json_object = get_object_or_404(CustomObject, title=title)
    return JsonResponse(json_object.json)


class SearchForm(forms.Form):
    q = AutoCompleteField('cliche',
                          required=True,
                          help_text="Autocomplete will suggest clichés about cats, but you can enter anything you like.",
                          label="Favorite Cliché",
                          attrs={'size': 100})


def search_form(request):
    dd = {}
    if 'q' in request.GET:
        dd['entered'] = request.GET.get('q')
    initial = {'q': "\"This is an initial value,\" said O'Leary."}
    form = SearchForm(initial=initial)
    dd['form'] = form
    return render_to_response('search_form.html', dd, context_instance=RequestContext(request))

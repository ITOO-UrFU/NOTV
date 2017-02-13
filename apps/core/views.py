from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CustomObject


def custom_json_view(request, title):
    json_object = get_object_or_404(CustomObject, title=title)
    return JsonResponse(json_object.json)



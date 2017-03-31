from django.db.models import Q
from django.utils.html import escape
from .models import Person
from ajax_select import LookupChannel
import ajax_select


class PersonLookup(LookupChannel):

    model = Person

    def get_query(self, q, request):
        return Person.objects.filter(Q(last_name__icontains=q) | Q(first_name__icontains=q)).order_by('last_name')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return str(obj)

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return escape(str(obj))

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return escape(str(obj))

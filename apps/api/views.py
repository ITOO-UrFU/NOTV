from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from django.contrib.auth.models import User

from core.models import *
from core.serializers import *


class Events(viewsets.ModelViewSet):
    queryset = Event.objects.filter(status="p")
    serializer_class = EventSerializer


class Persons(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by("-karma")
    serializer_class = PersonSerializer


class Users(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class Pages(viewsets.ModelViewSet):
    queryset = Page.objects.filter(status="p").order_by("weight")
    serializer_class = PageSerializer


class Paths(viewsets.ModelViewSet):
    queryset = Path.objects.all()
    serializer_class = PathSerializer



@api_view(('GET',))
def page_slug(request, slug):
    """
    Courses ids.
    """

    try:
        page = Page.objects.get(slug=slug)
    except:
        page = None

    if not page:
        try:
            page = Page.objects.get(pk=slug)
        except:
            page = None

    try:
        type = Type.objects.filter(pk=page.type.id).values("title").first()["title"]
    except:
        type = None

    if page:
        return Response({
            "id": page.id,
            "slug": page.slug,
            "title": page.title,
            "html": page.html,
            "pages": page.get_pages_dict(),
            "keywords": page.keywords,
            "type": type,
            "weight": page.weight,

        })
    else:
        raise Http404


class CreateUserView(CreateAPIView):
    model = User
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer


class UserList(ListCreateAPIView):
    """
    Return profile of current authenticated user or return 401.

    ### POST

    Create a new user account.
    Sends a confirmation mail if if PROFILE_EMAL_CONFIRMATION setting is True.

    **Required Fields**:

     * username
     * email
     * password
     * password_confirmation

    ** Optional Fields **

     * first_name
     * last_name
     * about
     * gender
     * birth_date
     * address
     * city
     * country
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    model = User
    serializer_class = UserCreateSerializer

    # custom
    serializer_reader_class = UserSerializer

    def get(self, request, *args, **kwargs):
        """ return profile of current user if authenticated otherwise 401 """
        serializer = self.serializer_reader_class

        if request.user.is_authenticated():
            return Response({'detail': serializer(request.user, context=self.get_serializer_context()).data})
        else:
            return Response({'detail': 'Authentication credentials were not provided'}, status=401)

    def post_save(self, obj, created):
        """
        Send email confirmation according to configuration
        """
        super(UserList, self).post_save(obj)

        if created:
            obj.add_email()



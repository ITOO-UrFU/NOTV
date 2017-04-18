from django.conf.urls import url, include
from django.contrib import admin

from rest_framework import routers
from django.views.generic import TemplateView

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token

from ajax_select import urls as ajax_select_urls

from api.views import *
from core.views import *
from stats.views import *

main_urlpatterns = []

main_urlpatterns += [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^custom/(?P<title>.*)/$', custom_json_view, name="custom_json_view"),
]
main_urlpatterns += [url(r'^api/v1/pages/(?P<slug>.*)/$', page_slug, name="page_slug"),
                     url(r'^api/v1/rest-auth/', include('rest_auth.urls')),
                     url(r'^api/v1/rest-auth/registration/', RegisterView.as_view(), name='rest_register'),
                     url(r'^api/v1/rest-auth/registration-students/', RegisterStudentView.as_view(), name='rest_register_student'),
                     url(r'^api/v1/account-confirm-email/(?P<key>[-:\w]+)/$', TemplateView.as_view(), name='account_confirm_email'),
                     url(r'^api/v1/api-token-auth/', obtain_jwt_token),
                     url(r'^api/v1/api-token-refresh/', refresh_jwt_token),
                     url(r'^api/v1/register/$', UserList.as_view(), name='api_profile_list'),
                     url(r'^api/v1/rest-auth/profile/$', PersonDetailsView.as_view(), name='profile'),
                     url(r'^api/v1/rest-auth/profile/update/$', PersonUpdate.as_view(), name='update_profile'),
                     url(r'^api/v1/rest-auth/events/register/$', register_on_event, name='register_on_event'),
                     url(r'^api/v1/rest-auth/events/unregister/$', unregister_on_event, name='unregister_on_event'),
                     url(r'^api/v1/rest-auth/events/event_user_list/$', event_user_list, name='event_user_list'),
                     url(r'^api/v1/docs/upload/$', file_upload, name="upload"),
                     url(r'^api/v1/docs/delete/$', delete_file, name='delete_file'),
                     url(r'^api/v1/reset_password/$', reset_password, name='reset_password'),
                     url(r'^api/v1/change_password/$', change_password, name='change_password'),
                     url(r'^admin/events_members/$', events_members, name='events_members'),

                     url(r'^search_form',
                         view=search_form,
                         name='search_form'),
                     url(r'^admin/lookups/', include(ajax_select_urls)),
                     ]

router = routers.DefaultRouter()
router.register(r'events', Events)
router.register(r'persons', Persons)
router.register(r'users', Users)
router.register(r'paths', Paths)
router.register(r'pages', Pages, base_name='pages')
router.register(r'speakers', Speakers, base_name='speakers')


main_urlpatterns.append(url(r'^api/v1/', include(router.urls, namespace='api')))

urlpatterns = [
    url(r'^edcrunch/', include(main_urlpatterns)),
]

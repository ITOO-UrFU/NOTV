"""notv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework import routers, serializers, viewsets

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token

from api.views import *
from core.views import custom_json_view


urlpatterns = []

urlpatterns += [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^custom/(?P<title>.*)/$', custom_json_view, name="custom_json_view"),
]
urlpatterns += [url(r'^api/v1/pages/(?P<slug>.*)/$', page_slug, name="page_slug"),
                url(r'^api/v1/rest-auth/', include('rest_auth.urls')),
                url(r'^api/v1/rest-auth/registration/', include('rest_auth.registration.urls')),
                url(r'^api/v1/api-token-auth/', obtain_jwt_token),
                url(r'^api/v1/api-token-refresh/', refresh_jwt_token),
                url(r'^api/v1/register/$', UserList.as_view(), name='api_profile_list'),
                ]

router = routers.DefaultRouter()
router.register(r'events', Events)
router.register(r'persons', Persons)
router.register(r'users', Users)
router.register(r'paths', Paths)
router.register(r'pages', Pages, base_name='pages')


urlpatterns.append(url(r'^api/v1/', include(router.urls, namespace='api')))

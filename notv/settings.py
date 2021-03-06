# *-* encoding: utf-8 *-*
import datetime
import os
import sys

from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'w)ag^7sm__op6jlq!el*u05d6%&#jzd9wl#k8c(=lozz&v0bb4'

DEBUG = True

ALLOWED_HOSTS = ["*", ]

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ajax_select',
    'reversion',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    'allauth',
    'allauth.account',
    'corsheaders',
    'admin_reorder',
    'core',
    'api',
    'stats',
]

REST_USE_JWT = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
DEFAULT_FROM_EMAIL = "no-reply@edcrunch.urfu.ru"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",

    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'notv.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'notv.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 2,
        }
    }
]

LANGUAGES = [
    ('ru', 'Russian'),
    ('en', 'English'),
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_L10N = False

USE_TZ = False

STATIC_URL = '/static/'

LOGIN_REDIRECT_URL = '/'

#### CORS ####
# CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
    '127.0.0.1:3000',
    'localhost:*',
    "*"
)

CORS_URLS_REGEX = r'^.*$'

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

#### REST FRAMEWORK ####

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

ADMIN_REORDER = (
    {'app': 'core', 'label': 'Мероприятия', 'models': (
        'core.Event',
        'core.EventType',
        'core.LineOfWork',
        'core.Room',
        'core.Path',
    )
     },
    {'app': 'core', 'label': 'Персона', 'models': ('core.Person',)},
    {'app': 'core', 'label': 'Страницы', 'models': ('core.Page',)},
    {'app': 'core', 'label': 'Связи', 'models': ('core.RegistrationType',
                                                 'core.EventUserRegistration')},
    {'app': 'core', 'label': 'Разное', 'models': ('core.CustomObject', "auth.User")},
    {'app': 'core', 'label': 'Публикации', 'models': ('core.Document',)},

)

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
        'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
        'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
        'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=14),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=14),

    'JWT_AUTH_HEADER_PREFIX': '',
}

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = 'https://openedu.urfu.ru/files/NOTV17/NOTV/staticfiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = 'https://openedu.urfu.ru/files/NOTV17/NOTV/media/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': '_cache',

        'TIMEOUT': 60 * 15,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 15
}

AJAX_LOOKUP_CHANNELS = {
    'person': ('core.lookups', 'PersonLookup'),
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

"""
Django settings for taskstack project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# Get secret key from env or create a random one
SECRET_KEY = os.getenv(
    'TASKSTACK_SECRET_KEY',
    ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
)

# If the env variable TASKSTACK_DEBUG has any value, set DEBUG to True
if os.getenv('TASKSTACK_DEBUG', False):
    DEBUG = True
    TEMPLATE_DEBUG = True
else:
    DEBUG = False
    TEMPLATE_DEBUG = False


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'taskstack.urls'

WSGI_APPLICATION = 'taskstack.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# Default database is on localhost but that's overridable with
# env variables.
database = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'taskstack',
    'USER': 'taskstack',
    'PASSWORD': 'taskstack',
    'HOST': '127.0.0.1',
    'PORT': '5432',
}

database['HOST'] = os.getenv('TASKSTACK_POSTGRES_HOST', '127.0.0.1')
database['NAME'] = os.getenv('TASKSTACK_POSTGRES_DATABASE', database['NAME'])
database['USER'] = os.getenv('TASKSTACK_POSTGRES_USER', database['USER'])
database['PASSWORD'] = os.getenv('TASKSTACK_POSTGRES_PASSWORD', database['PASSWORD'])

DATABASES = {
    'default': database
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/login'
LOGOUT_URL = '/logout'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'core.Member'


# Custom settings for Taskstack
DEFAULT_QUEUE_SIZE = 10

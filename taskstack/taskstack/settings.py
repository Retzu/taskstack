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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

# If the env variable TASKSTAK_DEBUG has any value, set DEBUG to True
if os.getenv('TASKSTAK_DEBUG', False):
    DEBUG = True
    TEMPLATE_DEBUG = True
else:
    DEBUG = False
    TEMPLATE_DEBUG = False


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'taskstack_core',
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

DOCKER_DB_HOST = 'taskstack-database'

# Set the database to either localhost (DB is running in a docker container)
# or a hostname (Django AND DB are running in docker containers like in prod)
# If Django is running in a container we can get the credentials from env. variables
database = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'taskstack',
    'USER': 'taskstack',
    'PASSWORD': 'taskstack',
    'HOST': '127.0.0.1',
    'PORT': '5432',
}

if not DEBUG:
    database['HOST'] = os.getenv('POSTGRES_DB', DOCKER_DB_HOST)
    database['USER'] = os.getenv('POSTGRES_USER', database['USER'])
    database['PASSWORD'] = os.getenv('POSTGRES_PASSWORD', database['PASSWORD'])

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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


# Custom settings for Taskstack
DEFAULT_QUEUE_SIZE = 10

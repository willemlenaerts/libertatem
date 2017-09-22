"""
Django settings for exergos project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mpjn+z)t_w0%nttcu$web9*@*br)^5qzgb@(gy$v%es23rs(%a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 3th party
    'compressor',
    
    # Own apps
    'website',
    'app_voornamen',
    'app_dodentocht',
    'app_voetbalelo',
    'app_voetbalpi',
    'app_georoute',
    'app_sentiment',
    'app_twitterscrape',
    'app_draw',
    'geodata'
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

ROOT_URLCONF = 'exergos.urls'

WSGI_APPLICATION = 'exergos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

# Local database
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'exergos',
            'USER': 'postgres',
            'PASSWORD': 'Will0870',
            'HOST': '0.0.0.0',
            'PORT':'5432'
        }
    }
    
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #         'NAME': 'dfhp8kghuppgs0',
    #         'USER': 'xnrwfxspekgnnj',
    #         'PASSWORD': 'qWrpH46M7581E7BiXKUIacPqzN',
    #         'HOST': 'ec2-107-22-253-198.compute-1.amazonaws.com',
    #         'PORT':'5432'
    #     }
    # }
# Production database
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT':''
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
    os.path.join(BASE_DIR, 'blog/templates/zinnia'),
    # os.path.join(BASE_DIR, 'mezzanine-master/mezzanine'),
    # os.path.join(BASE_DIR, 'mezzanine-master/mezzanine/blog/templates'),
)

# URL van static files
STATIC_URL = '/staticfiles/'

# Waar collectstatic alle static files gaat bewaren
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Van waar collectstatic allemaal static files moet gaan halen
STATICFILES_DIRS =  (os.path.join(BASE_DIR, "static"),)


# MEDIA_URL
MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

SITE_ID = 1

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.i18n',
  'django.core.context_processors.request',
  'zinnia.context_processors.version',  # Optional
)

TEMPLATE_LOADERS = (
    'app_namespace.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)
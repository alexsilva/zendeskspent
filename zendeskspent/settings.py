# coding=utf-8
"""
Django settings for zendeskspent project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import environ

root = environ.Path(__file__) - 2
env = environ.Env(DEBUG=(bool, False))  # set default values and casting
environ.Env.read_env()  # reading .env file

BASE_DIR = root()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

# Celery configs
BROKER_URL = env('BROKER_URL', default='amqp://')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='amqp')

ZENDESK_BASE_URL = 'https://{0!s}.zendesk.com'.format(env('ZENDESK_URL_COMPANY_NAME',
                                                          default="zendesk"))
ZENDESK_EMAIL = env('ZENDESK_EMAIL')
ZENDESK_PASSWORD = env('ZENDESK_PASSWORD')
ZENDESK_API_VERSION = env.int('ZENDESK_API_VERSION', default=2)

COMPANY_ESTIMATED_HOURS_ID = env.int('COMPANY_ESTIMATED_HOURS_ID', default=0)
COMPANY_SPENT_HOURS_ID = env.int('COMPANY_SPENT_HOURS_ID', default=0)

EXPORT_CSV_COLUMNS = ('Título', 'Criando em', 'Atualizado em', 'Horas gastas', 'Horas estimadas')

# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'contracts',
    'xadmin',
    'crispy_forms',
    'remotesyc',
    'django_js_reverse'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'zendeskspent.urls'

WSGI_APPLICATION = 'zendeskspent.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': env.db()
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')

DATETIME_FORMAT = env('DATETIME_FORMAT', default="d/m/Y H:i:s")
DATE_FORMAT = env('DATE_FORMAT', default="d/m/Y")

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# up root
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), os.path.basename(BASE_DIR) + '_staticfiles')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    root('static'),
)

TEMPLATE_DIRS = (
    root('templates'),
)

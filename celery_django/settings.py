"""
Django settings for web_app project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
import logging
import socket
log = logging.getLogger("web_app.applogger")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'web_app'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# noinspection SpellCheckingInspection
SECRET_KEY = 'blah-blah'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if 'productionserver' in socket.getfqdn():
    CURR_HOSTNAME = socket.getfqdn()
else:
    CURR_HOSTNAME = socket.getfqdn().replace('.dev.com', '')


ALLOWED_HOSTS = ['localhost', '127.0.0.1', CURR_HOSTNAME, socket.getfqdn()]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # 'django_celery_results',  # Disable if result_backend = 'django-db'
    'django_celery_beat',
    'bootstrap4',
    'web_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'static/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'web_app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
# https://stackoverflow.com/questions/26958592/django-after-upgrade-mysql-server-has-gone-away
# https://stackoverflow.com/questions/16946938/django-unknown-system-variable-transaction-on-syncdb
# noinspection SpellCheckingInspection
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'web_app_database',
        'USER': 'web_app_user',
        'PASSWORD': 'web_app_user_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'CONN_MAX_AGE': 3600,
        'OPTIONS': {
            'read_default_file': '/etc/my.cnf',
            # 'init_command': 'SET default_storage_engine=INNODB;'
            # 'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED',
            # 'init_command': 'SET default_storage_engine=INNODB',
        },
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(STATIC_ROOT, 'admin'),
)

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# https://docs.djangoproject.com/en/2.0/topics/email/
EMAIL_HOST = 'mail.dev.com'

# Django registration:
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# https://github.com/maxtepkeev/architect/issues/38
# https://github.com/celery/django-celery/issues/359
CONN_MAX_AGE = None

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# DEBUG OPT:
if os.name == "nt":
    log.debug("=========================================================")
    log.debug("PROJECT_ROOT:     %s", PROJECT_ROOT)
    log.debug("BASE DIR:         %s", BASE_DIR)
    log.debug("=========================================================")
    log.debug("TEMPLATES:        %s", TEMPLATES[0]['DIRS'][0])
    log.debug("Static root:      %s", STATIC_ROOT)
    log.debug("=========================================================")
    log.debug("SYS PATH: ", sys.path)
    log.debug("=========================================================")
    log.debug("STATICFILES_DIRS: %s", STATICFILES_DIRS)

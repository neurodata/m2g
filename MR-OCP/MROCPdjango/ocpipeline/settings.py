
# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created by Disa Mhembere
# Email: disa@jhu.edu
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module containing the settings for the django project
"""
import os.path

from settings_secret import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#ADMINS - moved

MANAGERS = ADMINS

# DATABASES - moved

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = '/data/ocp'
MEDIA_ROOT = '/mnt/nfs/indata/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/ocp/'

BASE_DIR = os.path.abspath(os.path.join(os.environ["M2G_HOME"], "MR-OCP", "MROCPdjango"))

# Directory containing templates
TEMPLATE_DIR = os.path.join(BASE_DIR, 'pipeline', 'templates/')
PROCESSING_SCRIPTS = os.path.join(os.environ["M2G_HOME"], "MR-OCP", "mrcap")

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

STATIC_ROOT = os.path.join(BASE_DIR,'pipeline', 'static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/graph-services/static/'

# DM for url resolution *MUST have a trailing slash /*
URL_BASE = "graph-services/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'pipeline', 'templates/static/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
# SECRET_KEY - moved

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

# DM Add for context processors in templates
TEMPLATE_CONTEXT_PROCESSORS = (
#    'django.core.context_processors.debug',
#    'django.core.context_processors.i18n',
#    'django.core.context_processors.media',
    'django.core.context_processors.request', # Access request data from template
    'django.core.context_processors.static', # {{STATIC_URL}}
    'django.contrib.auth.context_processors.auth', # For use with user An auth.User instance
#    'django.contrib.messages.context_processors.messages',
# Add method here that takes httpRequest & returns dict for custom context processors
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ocpipeline.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ocpipeline.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
    os.path.join(BASE_DIR,'pipeline', 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline', # DM
    'registration', # DM
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django_tables2',
    'djcelery',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# For invariant types
# The following are valid fileTypes:
# 0. 'lcc'|'lrgstConnComp' is largest connected component
# 1.'cc'|'clustCoeff' is the clustering coefficient
# 2.'deg'|'degree' is the local vertex degree
# 3.'eig'|'eigen' is the eigenvalues AND eigenvectors
# 4.'mad'|'maxAvgDeg' is the maximum average degree
# 5.'ss1'| 'scanStat1' is the scan statistic 1
# 6.'ss2'| 'scanStat2' is the scan statistic 2
# 7.'tri'|'triangle' is the triangle count
# 8.'fg'|'fibergraph' is a fibergraph built by gengraph.py
# 9.'apl'|'avePathLen' is the avergae path length
# 10. 'svd'|'singValDecomp' is the single value decomposition embedding

EQUIV_NP_ARRAYS = {'cc':'clustCoeff', 'deg':'degree', 'eig':'eigen', 'apl':'avePathLen',
                    'ss1': 'scanStat1','ss2': 'scanStat2','tri':'triangle','svd':'singValDecomp'}

VALID_FILE_TYPES = EQUIV_NP_ARRAYS
VALID_FILE_TYPES['mad'] = 'maxAvgDeg'
VALID_FILE_TYPES['fg'] = 'fibergraph'
VALID_FILE_TYPES['lcc'] = 'lrgstConnComp'
VALID_FILE_TYPES['gdia'] = 'graphDiam'

# Celery Settings
BROKER_URL = 'amqp://guest@localhost'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json', 'pickle']
CELERYD_PREFETCH_MULTIPLIER = 1

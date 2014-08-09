# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

import os

# importa os dados dependentes do ambiente
from networkapi.environment_settings import *

from networkapi.models.models_signal_receiver import *

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# Armazena a raiz do projeto.
SITE_ROOT = os.path.realpath(__file__ + "/../../../../")

TEMPLATE_DEBUG = DEBUG

API_VERSION = '15.96'

# On create group will associate the 'authenticate' permission automatically if 'True'
ASSOCIATE_PERMISSION_AUTOMATICALLY = True
ID_AUTHENTICATE_PERMISSION = 5

ADMINS = (
    ('Suporte Telecom', 'suptel@corp.globo.com'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {

    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'networkapi.log.CommonAdminEmailHandler'
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

MANAGERS = ADMINS

DEFAULT_CHARSET = 'utf-8'  # Set the encoding to database data

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '192.168.24.48:11211'
        ]
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-BR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ry@zgop%w80_nu83#!tbz)m&7*i@1)d-+ki@5^d#%6-&^216sg'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

if LOG_SHOW_SQL:
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
#        'django.contrib.sessions.middleware.SessionMiddleware',
#        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'networkapi.SQLLogMiddleware.SQLLogMiddleware',
        'networkapi.processExceptionMiddleware.LoggingMiddleware',
    )
else:
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'networkapi.processExceptionMiddleware.LoggingMiddleware',
#        'django.contrib.sessions.middleware.SessionMiddleware',
#        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )

ROOT_URLCONF = 'networkapi.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'templates')
)

INSTALLED_APPS = (
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
    'networkapi.ambiente',
    'networkapi.equipamento',
    'networkapi.eventlog',
    'networkapi.grupo',
    'networkapi.healthcheckexpect',
    'networkapi.interface',
    'networkapi.ip',
    'networkapi.requisicaovips',
    'networkapi.roteiro',
    'networkapi.tipoacesso',
    'networkapi.usuario',
    'networkapi.vlan',
    'networkapi.grupovirtual',
    'networkapi.models',
    'networkapi.filter',
    'networkapi.filterequiptype',
    'networkapi.blockrules',
#    'networkapi.test_form',
)


NETWORKAPI_VERSION = "1.0"

# Intervals to calculate the vlan_num in POST request /vlan/.
MIN_VLAN_NUMBER_01 = 2
MAX_VLAN_NUMBER_01 = 1001
MIN_VLAN_NUMBER_02 = 1006
MAX_VLAN_NUMBER_02 = 4094

# Intervals to calculate the oct4 of the IP in POST request /ip/.
MIN_OCT4 = 5
MAX_OCT4 = 250

TEST_RUNNER = 'django_pytest.test_runner.TestRunner'

##########
# # Scripts

# VLAN
VLAN_REMOVE = 'navlan -i %d --remove'
VLAN_CREATE = 'navlan -I %d -L2 --cria'

# REDE
NETWORKIPV4_CREATE = 'navlan -I %d --IPv4 --cria'
NETWORKIPV6_CREATE = 'navlan -I %d --IPv6 --cria'
NETWORKIPV4_REMOVE = 'navlan -I %d --IPv4 --remove'
NETWORKIPV6_REMOVE = 'navlan -I %d --IPv6 --remove'

VIP_CREATE = 'gerador_vips -i %d --cria'
VIP_REMOVE = 'gerador_vips -i %d --remove'

# VIP REAL
VIP_REAL_v4_CREATE = 'gerador_vips -i %s --real %s --ip %s --add'
VIP_REAL_v6_CREATE = 'gerador_vips -i %s --real %s --ipv6 %s --add'
VIP_REAL_v4_REMOVE = 'gerador_vips -i %s --real %s --ip %s --del'
VIP_REAL_v6_REMOVE = 'gerador_vips -i %s --real %s --ipv6 %s --del'
VIP_REAL_v4_ENABLE = 'gerador_vips -i %s --real %s --ip %s --ena'
VIP_REAL_v6_ENABLE = 'gerador_vips -i %s --real %s --ipv6 %s --ena'
VIP_REAL_v4_DISABLE = 'gerador_vips -i %s --real %s --ip %s --dis'
VIP_REAL_v6_DISABLE = 'gerador_vips -i %s --real %s --ipv6 %s --dis'
VIP_REAL_v4_CHECK = 'gerador_vips -i %s --real %s --ip %s --chk'
VIP_REAL_v6_CHECK = 'gerador_vips -i %s --real %s --ipsv6 %s --chk'

# VIP REAL - new calls
VIP_REALS_v4_CREATE = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --add'
VIP_REALS_v6_CREATE = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --add'
VIP_REALS_v4_REMOVE = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --del'
VIP_REALS_v6_REMOVE = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --del'
VIP_REALS_v4_ENABLE = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --ena'
VIP_REALS_v6_ENABLE = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --ena'
VIP_REALS_v4_DISABLE = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --dis'
VIP_REALS_v6_DISABLE = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --dis'
VIP_REALS_v4_CHECK = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --chk'
VIP_REALS_v6_CHECK = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --chk'


###################################
#    PATH ACLS
###################################

PATH_ACL = os.path.join(PROJECT_ROOT_PATH, 'ACLS/')
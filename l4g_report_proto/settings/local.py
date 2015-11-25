from l4g_report_proto.settings.base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'l4g-proto',
        'USER': 'l4gadmin',
        'HOST': 'localhost',
    }
}

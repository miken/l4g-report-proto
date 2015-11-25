from l4g_report_proto.settings.base import *

DEBUG = False
# Insert snippet from Heroku site here

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {
    'default': dj_database_url.config()
}


# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
# BASE_DIR already set in base.py
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

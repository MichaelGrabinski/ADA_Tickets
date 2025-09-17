import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-change-me')
DEBUG = os.environ.get('DEBUG', '1') == '1'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,apps.easthartfordct.gov').split(',')
INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages',
    'mozilla_django_oidc',
 'django.contrib.staticfiles',
 'riders.apps.RidersConfig',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'ada_portal.urls'


from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        BASE_DIR / 'riders' / 'templates',
        BASE_DIR / 'ada_portal' / 'templates',
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]





WSGI_APPLICATION = 'ada_portal.wsgi.application'
DATABASES = {'default':{
    'ENGINE':'mssql',
    'NAME':os.environ.get('DB_NAME','ADA_Tickets'),
    'USER':os.environ.get('DB_USER','Michael'),
    'PASSWORD':os.environ.get('DB_PASSWORD','D3lt@kil0'),
    'HOST':os.environ.get('DB_HOST','TOEHIT-APPS-LT'),
    'PORT':os.environ.get('DB_PORT','1433'),
    'OPTIONS': {
    'driver': 'ODBC Driver 18 for SQL Server',
    # Pass raw ODBC attributes via extra_params
    'extra_params': 'Encrypt=yes;TrustServerCertificate=yes;'
}

}}
AUTHENTICATION_BACKENDS = [
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend','django.contrib.auth.backends.ModelBackend',
]


LOGIN_URL = '/oidc/authenticate/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'



STATIC_URL = 'static/'             # or '/static/'
STATICFILES_DIRS = [BASE_DIR / 'riders' / 'static']  # optional; create the folder or remove this line
# For production (optional):
# STATIC_ROOT = BASE_DIR / 'staticfiles'



import os

TENANT_ID = os.environ.get('AZURE_TENANT_ID')
OIDC_RP_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
OIDC_RP_SCOPES = 'openid profile email'
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_STORE_ACCESS_TOKEN = True
OIDC_STORE_ID_TOKEN = True
OIDC_USE_NONCE = True

# Discovery (simplest):
OIDC_OP_DISCOVERY_ENDPOINT = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"








'''
TENANT_ID = os.environ.get('AZURE_TENANT_ID','YOUR_TENANT_ID')
OIDC_RP_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID','YOUR_APP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET','YOUR_APP_CLIENT_SECRET')
OIDC_RP_SCOPES = 'openid profile email'
OIDC_OP_DISCOVERY_ENDPOINT = f'https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration'
LOGIN_URL = '/oidc/authenticate/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
OIDC_STORE_ACCESS_TOKEN = True
OIDC_STORE_ID_TOKEN = True
OIDC_USE_NONCE = True
SESSION_COOKIE_SECURE = False if DEBUG else True
CSRF_COOKIE_SECURE = False if DEBUG else True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR/'riders'/'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
'''

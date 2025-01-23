from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url


ENV = os.getenv('ENV', 'development') # defaults to development, server is set to 'production'

# Load environment variables from .env file
if ENV == 'development':
    load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV == 'development'

if ENV == 'development':
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = ['makemymealplan.com', 'www.makemymealplan.com', '167.71.130.88']
    CSRF_TRUSTED_ORIGINS = ['https://makemymealplan.com', 'https://www.makemymealplan.com', 'https://167.71.130.88']
    CSRF_COOKIE_SECURE = True  # Only if using HTTPS
    SESSION_COOKIE_SECURE = True  # Only if using HTTPS
    SESSION_COOKIE_DOMAIN = ".makemymealplan.com"
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # For reverse proxies

# Application definition

INSTALLED_APPS = [
    'planner',
    'template_partials',
    'django_browser_reload',
    'django.contrib.admin',
    'django.contrib.auth',
    'allauth',
    'allauth.account',
    # 'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'imagekit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'planner.middleware.LoginRequiredMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',  
                'django.template.context_processors.request',          
                ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

if ENV == 'production':
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL')
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': '',
            'EMAIL_AUTHENTICATION': True,
            'SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT': True,
        }
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL= 'erik@eriklonnroth.com'
DEFAULT_SERVER_EMAIL= os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')


ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_DISPLAY = 'user.email'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL='https'

LOGIN_REDIRECT_URL = '/'



# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# S3/DO Spaces settings
AWS_ACCESS_KEY_ID = os.getenv('DO_SPACES_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('DO_SPACES_SECRET')
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_REGION_NAME = 'lon1'
AWS_S3_ENDPOINT_URL = 'https://lon1.digitaloceanspaces.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

if ENV == 'development':
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    MEDIA_URL = 'https://erik.lon1.digitaloceanspaces.com/mmp/media/'

    STORAGES = {
        'default': {
            'BACKEND': 'planner.services.s3_storage.MediaStorage', # uses s3boto3
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
from pathlib import Path
from json import load

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-2&_49v#j%8288fm-y(9fogao*lz)c7#=q-=y_2^xdcs21iaxs('

DEBUG = True

ALLOWED_HOSTS = ['51.68.140.249', 'https://nykram.pl', 'localhost', '127.0.0.1', 'nykram.pl']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'smite_lore',
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

ROOT_URLCONF = 'smite_lore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smite_lore.wsgi.application'

with open('dbconfig.json', 'r') as file:
    config = load(file)

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': config['database']['dbname'],
        'USER': config['database']['login'],
        'PASSWORD': config['database']['password'],
        'HOST': config['database']['server_name'],
        'PORT': "1433",
        "OPTIONS": {'driver': 'ODBC Driver 17 for SQL Server'},
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

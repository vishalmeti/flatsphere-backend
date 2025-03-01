"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",  # Django REST framework
    "corsheaders",  # Django CORS headers
    "users",  # USERS app
    "workspaces",  # WORKSPACES app
    "media",  # MEDIA app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASE_URL = config('DATABASE_URL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE_URL.split('/')[-1],
        'USER': DATABASE_URL.split('://')[1].split(':')[0],
        'PASSWORD': DATABASE_URL.split('://')[1].split(':')[1].split('@')[0],
        'HOST': DATABASE_URL.split('@')[1].split(':')[0],
        'PORT': DATABASE_URL.split(':')[-1].split('/')[0],
    }
}

# settings.py
AUTH_USER_MODEL = 'users.User'


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js (development)
    "https://yourdomain.com",  # Your production frontend URL
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=360),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.CustomTokenObtainPairSerializer",
}

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')  # Your AWS access key
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')  # Your AWS secret key
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")  # Your S3 bucket name
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-north-1')  # Your bucket region
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'  # Optional: Custom domain for files

# File Storage Settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# Optional: Set permissions for uploaded files
AWS_QUERYSTRING_AUTH = False  # Don't add authentication parameters to URLs

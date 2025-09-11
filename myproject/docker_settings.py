from .settings import *
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database settings for Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Static files settings
STATIC_ROOT = '/app/static'

# Media files settings
MEDIA_ROOT = '/app/media'

# Allowed hosts for Docker
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

# Debug setting
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Secret key from environment
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

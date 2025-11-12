from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': env('DB_NAME', default='aime'),
        'USER': env('DB_USER', default='sreeraj'),
        'PASSWORD': env('DB_PASSWORD', default='nic*123'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='3306'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

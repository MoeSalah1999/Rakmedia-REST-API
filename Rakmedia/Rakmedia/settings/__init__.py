from .dev import *
import os
env_setting = os.getenv('DJANGO_SETTINGS_MODULE')

if not env_setting:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rakmedia.settings.dev')


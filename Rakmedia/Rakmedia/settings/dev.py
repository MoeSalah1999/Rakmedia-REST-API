
from .base import *

DEBUG = True

# If you want Redis in dev, override here. Example:
# Q_CLUSTER.update({
#     "orm": None,
#     "broker": "redis://localhost:6379/0",
#     "redis": {"host": "localhost", "port": 6379, "db": 0}
# })

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "debug_toolbar",
    "silk",
]

AUTH_USER_MODEL = 'api.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "silk.middleware.SilkyMiddleware",
]

#SILKY_INTERCEPT_FUNC = lambda request: not request.path.startswith("/admin/")

INTERNAL_IPS = [
    "127.0.0.1",
]

# Example development DB
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Development CORS and email settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "admin@example.com"


from .base import *
import os
import dj_database_url

# ==========================================================
# GENERAL
# ==========================================================
DEBUG = False

# Use environment variable for allowed hosts
# e.g. DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")

# ==========================================================
# DATABASE
# ==========================================================
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", "postgres://postgres:postgres@db:5432/postgres"),
        conn_max_age=600,
    )
}

# ==========================================================
# AUTHENTICATION
# ==========================================================
AUTH_USER_MODEL = "api.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# ==========================================================
# STATIC & MEDIA FILES
# ==========================================================
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ==========================================================
# SECURITY
# ==========================================================
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True") == "True"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True") == "True"
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ==========================================================
# EMAIL CONFIGURATION
# ==========================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# ==========================================================
# DJANGO Q CONFIGURATION (REDIS BACKEND)
# ==========================================================
Q_CLUSTER.update({
    "name": "rakmedia",
    "orm": None,  # Use Redis as broker, not Django ORM
    "retry": 600,
    "timeout": int(os.environ.get("Q_TIMEOUT", 90)),
    "workers": int(os.environ.get("Q_WORKERS", 8)),
    "bulk": 10,
    "catch_up": False,
    "broker": os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    "redis": {
        "host": os.environ.get("REDIS_HOST", "redis"),
        "port": int(os.environ.get("REDIS_PORT", 6379)),
        "db": int(os.environ.get("REDIS_DB", 0)),
    },
})

# ==========================================================
# LOGGING
# ==========================================================
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": LOG_DIR / "django.log",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
}

# ==========================================================
# OPTIONAL INTEGRATIONS (future-ready)
# ==========================================================
# Example for Sentry integration (error monitoring):
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# sentry_sdk.init(
#     dsn=os.getenv("SENTRY_DSN"),
#     integrations=[DjangoIntegration()],
#     traces_sample_rate=1.0,
#     send_default_pii=True
# )

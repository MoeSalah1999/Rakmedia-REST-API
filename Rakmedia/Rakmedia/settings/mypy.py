from .dev import *

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS
    if app not in {
        "django_q",
    }
]

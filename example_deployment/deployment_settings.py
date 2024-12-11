import os

from drunc_ui.settings._production import *

ALLOWED_HOSTS = ["localhost"]
ADMINS = [("Chris", "c.cave-ayland@imperial.ac.uk")]

# email settings using an on premise SMTP server provided by imperial
EMAIL_HOST = "smarthost.cc.ic.ac.uk"
SERVER_EMAIL = "noreply@imperial.ac.uk"
DEFAULT_FROM_EMAIL = "noreply@imperial.ac.uk"

# database settings - will depend on your choice in deployment
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "drunc_ui",
        "USER": "drunc_ui",
        "PASSWORD": os.environ["DATABASE_PASSWORD"],
        "HOST": "db",
        "PORT": "5432",
    }
}

# a basic example logging configuration with environment variable support
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

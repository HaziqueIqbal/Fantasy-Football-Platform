from .base import *  # noqa: F401, F403
from .base import DEFAULT_MIDDLEWARE, THIRD_PARTY_MIDDLEWARE, env

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

CORS_ALLOW_ALL_ORIGINS = True

LOCAL_MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

MIDDLEWARE = DEFAULT_MIDDLEWARE + THIRD_PARTY_MIDDLEWARE + LOCAL_MIDDLEWARE

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

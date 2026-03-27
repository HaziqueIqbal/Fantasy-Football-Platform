from .base import *  # noqa: F401, F403
from .base import DEFAULT_MIDDLEWARE, env

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

CORS_ALLOW_ALL_ORIGINS = True

# WhiteNoise must sit immediately after SecurityMiddleware (index 0).
MIDDLEWARE = (
    DEFAULT_MIDDLEWARE[:1]
    + ["whitenoise.middleware.WhiteNoiseMiddleware"]
    + DEFAULT_MIDDLEWARE[1:]
)

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

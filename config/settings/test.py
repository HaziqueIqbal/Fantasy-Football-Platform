from .base import *  # noqa: F401, F403
from .base import DEFAULT_MIDDLEWARE, THIRD_PARTY_MIDDLEWARE

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

MIDDLEWARE = DEFAULT_MIDDLEWARE + THIRD_PARTY_MIDDLEWARE

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

DEFAULT_FILE_STORAGE = "django.core.files.storage.InMemoryStorage"

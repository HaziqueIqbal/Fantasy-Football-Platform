from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "0.0.0.0", "127.0.0.1"]),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR}/db.sqlite3"),
    SECRET_KEY=(str, ""),
    ACCESS_TOKEN_LIFETIME_MINUTES=(int, 60),
    REFRESH_TOKEN_LIFETIME_DAYS=(int, 7),
    DEFAULT_PAGE_LIMIT=(int, 15),
    TRANSFER_VALUE_INCREASE_MIN=(int, 10),
    TRANSFER_VALUE_INCREASE_MAX=(int, 100),
)

env.read_env(str(BASE_DIR / ".env"), overwrite=False)

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
]

LOCAL_APPS = [
    "fantasyfootball.user",
    "fantasyfootball.team",
    "fantasyfootball.player",
    "fantasyfootball.transfer",
    "fantasyfootball.transaction",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "user.User"

DEFAULT_MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

THIRD_PARTY_MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# -------------------------------------------------------------------
# JWT
# -------------------------------------------------------------------
ACCESS_TOKEN_LIFETIME_MINUTES = env("ACCESS_TOKEN_LIFETIME_MINUTES")
REFRESH_TOKEN_LIFETIME_DAYS = env("REFRESH_TOKEN_LIFETIME_DAYS")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# -------------------------------------------------------------------
# Django REST Framework
# -------------------------------------------------------------------
DEFAULT_PAGE_LIMIT = env("DEFAULT_PAGE_LIMIT")

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "fantasyfootball.common.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "EXCEPTION_HANDLER": "fantasyfootball.common.exception_handler.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "fantasyfootball.common.pagination.StandardResultsPagination",
    "PAGE_SIZE": DEFAULT_PAGE_LIMIT,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# -------------------------------------------------------------------
# OpenAPI / Swagger
# -------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Fantasy Football Platform API",
    "DESCRIPTION": "Backend API for Fantasy Football Platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {
        "PlayerPositionEnum": "fantasyfootball.player.models.Player.Position",
    },
    "SECURITY": [{"bearerAuth": []}],
}

# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------

CORS_URLS_REGEX = r"^/api/.*$"

# -------------------------------------------------------------------
# Fantasy Football domain constants
# -------------------------------------------------------------------
TEAM_INITIAL_BUDGET = 5_000_000
PLAYER_INITIAL_VALUE = 1_000_000
TEAM_SIZE = 20
PLAYER_DISTRIBUTION = {
    "goalkeeper": 3,
    "defender": 5,
    "midfielder": 6,
    "attacker": 6,
}

TRANSFER_VALUE_INCREASE_MIN = env("TRANSFER_VALUE_INCREASE_MIN")
TRANSFER_VALUE_INCREASE_MAX = env("TRANSFER_VALUE_INCREASE_MAX")

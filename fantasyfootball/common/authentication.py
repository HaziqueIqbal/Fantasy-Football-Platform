from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .exceptions import AuthenticationFailedException


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate using JWT from the Authorization header (Bearer token)
    or, as a fallback, from the 'access' cookie.
    """

    def authenticate(self, request):
        header = self.get_header(request)

        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get("access")

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError):
            raise AuthenticationFailedException()

        return self.get_user(validated_token), validated_token


class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """Register CookieJWTAuthentication with drf-spectacular."""

    target_class = "fantasyfootball.common.authentication.CookieJWTAuthentication"
    name = "bearerAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT access token. Pass as 'Authorization: Bearer <token>' "
                "header or as the 'access' cookie."
            ),
        }

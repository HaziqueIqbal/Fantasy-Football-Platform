import logging

from django.contrib.auth import authenticate
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from fantasyfootball.common.utils import format_response

from .serializers import (
    TokenPairSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserProfileSerializer},
        tags=["Auth"],
        summary="Register a new user",
        description="Creates a user account plus a team of 20 players automatically.",
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = TokenPairSerializer.for_user(user)
        data = {
            "user": UserProfileSerializer(user).data,
            "tokens": tokens,
        }
        return format_response(
            data=data,
            message="User registered successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserProfileSerializer},
        tags=["Auth"],
        summary="Login",
        description="Authenticate with email and password. Returns JWT access and refresh tokens.",
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return format_response(
                data=None,
                message="Invalid email or password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False,
            )

        tokens = TokenPairSerializer.for_user(user)
        data = {
            "user": UserProfileSerializer(user).data,
            "tokens": tokens,
        }
        logger.info("User %s logged in.", user.email)
        return format_response(
            data=data,
            message="Login successful.",
            status_code=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        summary="Logout",
        description="Blacklists the provided refresh token.",
        request=inline_serializer(
            "LogoutRequest", fields={"refresh": serializers.CharField()}
        ),
        responses={200: OpenApiResponse(description="Logged out successfully.")},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return format_response(
                data=None,
                message="Refresh token is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return format_response(
                data=None,
                message="Invalid or expired refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
            )

        logger.info("User %s logged out.", request.user.email)
        return format_response(
            data=None,
            message="Logged out successfully.",
            status_code=status.HTTP_200_OK,
        )


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Refresh access token",
        request=inline_serializer(
            "TokenRefreshRequest", fields={"refresh": serializers.CharField()}
        ),
        responses={
            200: inline_serializer(
                "TokenRefreshResponse",
                fields={
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            )
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return format_response(
                data=None,
                message="Refresh token is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
            )

        try:
            refresh = RefreshToken(refresh_token)
            data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        except TokenError:
            return format_response(
                data=None,
                message="Invalid or expired refresh token.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False,
            )

        return format_response(
            data=data,
            message="Token refreshed successfully.",
            status_code=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserProfileSerializer},
        tags=["User"],
        summary="Get my profile",
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return format_response(
            data=serializer.data,
            message="Profile retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        tags=["User"],
        summary="Update my profile",
    )
    def put(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return format_response(
            data=serializer.data,
            message="Profile updated successfully.",
            status_code=status.HTTP_200_OK,
        )

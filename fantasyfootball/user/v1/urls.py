from django.urls import path

from .views import LoginView, LogoutView, ProfileView, RegisterView, TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", ProfileView.as_view(), name="user-profile"),
]

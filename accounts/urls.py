from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import edit_profile

urlpatterns = [
    path("login/", views.student_login, name="student_login"),
    path("signup/", views.student_signup, name="student_signup"),
    path("logout/", views.student_logout, name="student_logout"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("profile/edit/", edit_profile, name="edit_profile"),
    # ✅ SECURE PASSWORD RESET FLOW
    path(
        "forgot-password/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/forgot_password.html"
        ),
        name="forgot_password",
    ),
    path(
        "forgot-password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
from .views import edit_profile


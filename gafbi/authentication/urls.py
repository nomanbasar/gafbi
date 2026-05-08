from django.urls import path

from .views import (
    SignupView,
    VerifyEmailView,
    LoginView,
    ResendEmailVerifyOtpView,
    ForgotPasswordView,
    ResendForgotPasswordOtpView,
    VerifyForgotPasswordOtpView,
    ResetPasswordView,
    ChangePasswordView,
    AdminProfileView,
    AdminProfileUpdateView,
)

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),
    path("login/", LoginView.as_view()),
    path("resend-email-verify-otp/", ResendEmailVerifyOtpView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("resend-forgot-password/", ResendForgotPasswordOtpView.as_view()),
    path("verify-forgot-password-otp/", VerifyForgotPasswordOtpView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),
    path("admin/profile/", AdminProfileView.as_view()),
    path("admin/profile/update/", AdminProfileUpdateView.as_view()),
]
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    SignupSerializer,
    VerifyEmailSerializer,
    LoginSerializer,
    ResendEmailVerifyOtpSerializer,
    ForgotPasswordSerializer,
    ResendForgotPasswordOtpSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    VerifyForgotPasswordOtpSerializer
)


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {"success": True, "message": "signup_otp_sent", "data": data},
            status=status.HTTP_201_CREATED
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {"success": True, "message": "email_verified", "data": data},
            status=status.HTTP_200_OK
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {"success": True, "message": "login_success", "data": data},
            status=status.HTTP_200_OK
        )


class ResendEmailVerifyOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendEmailVerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {"success": True, "message": "email_verify_otp_resent", "data": data},
            status=status.HTTP_200_OK
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {"success": True, "message": "forgot_password_otp_sent", "data": data},
            status=status.HTTP_200_OK
        )


class ResendForgotPasswordOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendForgotPasswordOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {"success": True, "message": "forgot_password_otp_resent", "data": data},
            status=status.HTTP_200_OK
        )


class VerifyForgotPasswordOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyForgotPasswordOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {
                "success": True,
                "message": "forgot_password_otp_verified",
                "data": data
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {"success": True, "message": "password_reset_success", "data": data},
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(
            {"success": True, "message": "password_changed_success", "data": data},
            status=status.HTTP_200_OK
        )
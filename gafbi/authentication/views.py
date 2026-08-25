from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    SignupSerializer,
    VerifyEmailSerializer,
    LoginSerializer,
    ResendEmailVerifyOtpSerializer,
    ForgotPasswordSerializer,
    ResendForgotPasswordOtpSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    VerifyForgotPasswordOtpSerializer,
    AdminProfileSerializer,
    AdminProfileUpdateSerializer,
    user_response,
)

from .utils import (
    move_refresh_token_to_cookie,
    set_refresh_cookie,
    delete_refresh_cookie,
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

        response = Response(
            {
                "success": True,
                "message": "email_verified",
                "data": data
            },
            status=status.HTTP_200_OK
        )

        return move_refresh_token_to_cookie(
            response,
            data
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        response = Response(
            {
                "success": True,
                "message": "login_success",
                "data": data
            },
            status=status.HTTP_200_OK
        )

        return move_refresh_token_to_cookie(
            response,
            data
        )


class RefreshAccessTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(
            settings.AUTH_REFRESH_COOKIE_NAME
        )

        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Already Logout. Please login Again",
                    "data": {},
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = TokenRefreshSerializer(
            data={
                "refresh": refresh_token
            }
        )

        try:
            serializer.is_valid(
                raise_exception=True
            )

        except (
            TokenError,
            AuthenticationFailed,
        ):
            response = Response(
                {
                    "success": False,
                    "message": "refresh_token_invalid",
                    "data": {},
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

            return delete_refresh_cookie(
                response
            )

        response = Response(
            {
                "success": True,
                "message": "token_refreshed",
                "data": {
                    "tokens": {
                        "access": serializer.validated_data[
                            "access"
                        ]
                    }
                },
            },
            status=status.HTTP_200_OK
        )

        new_refresh_token = (
            serializer.validated_data.get(
                "refresh"
            )
        )

        if new_refresh_token:
            set_refresh_cookie(
                response,
                new_refresh_token
            )

        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(
            settings.AUTH_REFRESH_COOKIE_NAME
        )

        if refresh_token:
            try:
                RefreshToken(
                    refresh_token
                ).blacklist()

            except TokenError:
                pass

        response = Response(
            {
                "success": True,
                "message": "logout_success",
                "data": {},
            },
            status=status.HTTP_200_OK
        )

        return delete_refresh_cookie(
            response
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

        response = Response(
            {
                "success": True,
                "message": "forgot_password_otp_verified",
                "data": data
            },
            status=status.HTTP_200_OK
        )

        return move_refresh_token_to_cookie(
            response,
            data
        )


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ResetPasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        response = Response(
            {
                "success": True,
                "message": "password_reset_success",
                "data": data
            },
            status=status.HTTP_200_OK
        )

        return move_refresh_token_to_cookie(
            response,
            data
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

        response = Response(
            {
                "success": True,
                "message": "password_changed_success",
                "data": data
            },
            status=status.HTTP_200_OK
        )

        return move_refresh_token_to_cookie(
            response,
            data
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "success": True,
                "message": "user_fetched",
                "data": {
                    "user": user_response(request.user)
                }
            },
            status=status.HTTP_200_OK
        )
    

class AdminProfileView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        serializer = AdminProfileSerializer(
            request.user,
            context={"request": request}
        )

        return Response({
            "success": True,
            "message": "admin_profile_fetched",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AdminProfileUpdateView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        serializer = AdminProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = AdminProfileSerializer(
            request.user,
            context={"request": request}
        )

        return Response({
            "success": True,
            "message": "admin_profile_updated",
            "data": response_serializer.data
        }, status=status.HTTP_200_OK)

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .serializers import RegisterSerializer, TokenSerializer
from .services import send_verification_email


User = get_user_model()


class RegisterView(APIView):

    @extend_schema(
        request=RegisterSerializer,
        responses={
            200: OpenApiResponse(description="Email sent successfully")
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        if user.is_active:
            return Response({
                "error": "User with this email already exists"
            }, status=status.HTTP_400_BAD_REQUEST)

        send_verification_email(user)

        return Response({
            "message": "Check your email to verify account"
        })


class VerifyEmailView(APIView):

    @extend_schema(
        parameters=[
            OpenApiParameter(name="uid", type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name="token", type=str, location=OpenApiParameter.PATH),
        ],
        responses={
            200: OpenApiResponse(description="Email confirmed")
        }
    )
    def get(self, request, uid, token):
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(id=user_id)
        except:
            return Response({"error": "invalid"}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "verified"})

        return Response({"error": "invalid token"}, status=400)


class LoginView(TokenObtainPairView):
    serializer_class = TokenSerializer

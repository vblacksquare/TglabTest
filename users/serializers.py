
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField()

    class Meta:
        model = User
        fields = ["email", "name", "password"]

    def create(self, validated_data):
        email = validated_data.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            return user

        return User.objects.create_user(
            is_active=False,
            **validated_data
        )


class TokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        if not user.is_active:
            raise AuthenticationFailed("Email not verified")

        return data

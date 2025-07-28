from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
import phonenumbers


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'title', 'slug', 'description', 'image', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone(self, value):
        try:
            value = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            phone_obj = phonenumbers.parse(value, "KG")
            if not phonenumbers.is_valid_number(phone_obj):
                raise serializers.ValidationError("Неверный номер телефона")
            return phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Номер телефона не распознан")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")

        user = authenticate(phone=phone, password=password)
        if not user:
            raise serializers.ValidationError("Неверный номер телефона или пароль")
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт отключён")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

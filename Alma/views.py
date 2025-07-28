from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
import random
from .signals import send_telegram_code

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            code = str(random.randint(100000, 999999))
            user.code = code
            user.save()
            send_telegram_code(code, user.phone)
            return Response({'message': 'Код отправлен в Telegram'}, status=201)
        return Response(serializer.errors, status=400)


class VerifyCodeView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        try:
            user = User.objects.get(phone=phone)
            if user.code == code:
                user.is_phone_verified = True
                user.code = ''
                user.save()
                return Response({'message': 'Номер подтверждён'})
            return Response({'error': 'Неверный код'}, status=400)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        try:
            user = User.objects.get(phone=phone)
            code = str(random.randint(100000, 999999))
            user.code = code
            user.save()
            send_telegram_code(code, phone)
            return Response({'message': 'Код для сброса пароля отправлен'}, status=200)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с таким номером не найден'}, status=404)


class ResetPasswordView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(phone=phone)
            if user.code == code:
                user.set_password(new_password)
                user.code = ''
                user.save()
                return Response({'message': 'Пароль успешно изменён'}, status=200)
            return Response({'error': 'Неверный код'}, status=400)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)



class BoardViewSet(viewsets.ReadOnlyModelViewSet): 
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.AllowAny]


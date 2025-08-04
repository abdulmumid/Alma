from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework_simplejwt.tokens import RefreshToken
import random
from .serializers import *
from .models import *
from .signals import send_telegram_code


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            code = str(random.randint(100000, 999999))
            user.code = code
            user.save()
            send_telegram_code(code, user.phone)
            return Response({'message': 'Код отправлен в Telegram'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if user.code == code:
            user.is_phone_verified = True
            user.code = ''
            user.save()
            return Response({'message': 'Номер подтверждён'})
        return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с таким номером не найден'}, status=status.HTTP_404_NOT_FOUND)

        code = str(random.randint(100000, 999999))
        user.code = code
        user.save()
        send_telegram_code(code, phone)
        return Response({'message': 'Код для сброса пароля отправлен'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if user.code == code:
            user.set_password(new_password)
            user.code = ''
            user.save()
            return Response({'message': 'Пароль успешно изменён'}, status=status.HTTP_200_OK)
        return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)


class BoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['barcode']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.AllowAny]


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()


    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserBonusViewSet(viewsets.ModelViewSet):
    queryset = UserBonus.objects.all()
    serializer_class = UserBonusSerializer
    permission_classes = [permissions.IsAuthenticated]


class NearestStoreView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lon = float(request.query_params.get('lon'))
        except (TypeError, ValueError):
            return Response({'error': 'Некорректные координаты'}, status=status.HTTP_400_BAD_REQUEST)

        user_location = Point(lon, lat, srid=4326)

        nearest_store = Store.objects.annotate(
            distance=Distance('location', user_location)
        ).order_by('distance').first()

        if nearest_store:
            data = StoreSerializer(nearest_store).data
            data['distance_km'] = round(nearest_store.distance.km, 2)
            return Response(data)
        return Response({'error': 'Магазины не найдены'}, status=status.HTTP_404_NOT_FOUND)


class CheckPriceView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        barcode = request.query_params.get('barcode')
        if not barcode:
            return Response({'error': 'Штрихкод обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        product = Product.objects.filter(barcode=barcode).first()
        if product:
            return Response(ProductSerializer(product).data)
        return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

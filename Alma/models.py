from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.contrib.gis.db import models as geomodels
import qrcode
from io import BytesIO
from django.core.files import File

# 🧑‍💼 Менеджер пользователя
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Номер телефона обязателен")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)

# 👤 Кастомная модель пользователя
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    phone = models.CharField("Телефон", max_length=20, unique=True)
    is_phone_verified = models.BooleanField("Телефон подтверждён", default=False)
    code = models.CharField("Код подтверждения", max_length=6, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Сотрудник", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def generate_qr_code(self):
        qr_data = f"User:{self.pk}, Phone:{self.phone}"
        qr_image = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        file_name = f"user_{self.pk}_qr.png"
        self.qr_code.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class Board(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("URL (slug)", unique=True, blank=True)
    description = RichTextUploadingField("Описание")
    image = models.ImageField("Изображение", upload_to='boards/')
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Доска"
        verbose_name_plural = "Доски"

class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    discount = models.DecimalField("Скидка", max_digits=5, decimal_places=2, null=True, blank=True)
    image = models.ImageField("Изображение", upload_to='products/')
    barcode = models.CharField("Штрихкод", max_length=100, unique=True)
    label = models.CharField("Начисленные бонусы", max_length=50, blank=True)
    is_featured = models.BooleanField("Избранный", default=False)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Магазин")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.barcode})"

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

class Stock(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    image = models.ImageField("Изображение", upload_to='stock/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

class Story(models.Model):
    title = models.CharField("Заголовок", max_length=100)
    icon = models.ImageField("Иконка", upload_to='stories/')
    is_active = models.BooleanField("Активный", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Сторис"
        verbose_name_plural = "Сторисы"

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField("Количество", default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product} ×{self.quantity}"

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Корзина"

class UserBonus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    bonuses = models.PositiveIntegerField("Бонусы", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} — {self.bonuses} бонусов"

    class Meta:
        verbose_name = "Бонус пользователя"
        verbose_name_plural = "Бонусы пользователей"

class Store(models.Model):
    name = models.CharField("Название магазина", max_length=255)
    location = geomodels.PointField("Координаты")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


# Менеджер пользователя
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

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(phone, password, **extra_fields)

# Кастомная модель пользователя
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    phone = models.CharField("Телефон", max_length=20, unique=True)
    is_phone_verified = models.BooleanField("Телефон подтверждён", default=False)
    code = models.CharField("Код подтверждения", max_length=6, blank=True)

    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Сотрудник", default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

# Модель доски
class Board(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('URL (slug)', unique=True, blank=True)
    description = RichTextUploadingField('Описание')
    image = models.ImageField('Изображение', upload_to='boards/')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'


class Product(models.Model):
    name = models.CharField(('Название'),max_length=255)
    price = models.DecimalField(('Цена'),max_digits=8, decimal_places=2)
    discount = models.DecimalField(('Скидка'),max_digits=5, decimal_places=2, null=True, blank=True)
    image = models.ImageField(('Изоброжение'),upload_to='products/')
    barcode = models.CharField(('Штрихкод'),max_length=100, unique=True)  # Штрих-код
    label = models.CharField(('Начисленные бонусы'),max_length=50, blank=True)      # например: "100 бонусов"
    is_featured = models.BooleanField(('Избронный'),default=False)

    def __str__(self):
        return f"{self.name} ({self.barcode})"
    
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class Stock(models.Model):
    title = models.CharField(('Зоголовок'), max_length=255)
    image =models.ImageField(('Изоброжение'), upload_to='Stock/')
    created_at = models.DateTimeField(('Время создания'), auto_now_add=True)

    def __str__(self):
        return f"{self.title}"
        
    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'


class Story(models.Model):
    title = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='stories/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"
        
    class Meta:
        verbose_name = 'Сторис'
        verbose_name_plural = 'Сторисы'


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product}"
        
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
 

class UserBonus(models.Model): 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bonuses = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user}"
        
    class Meta:
        verbose_name = 'Бонус пользователя'
        verbose_name_plural = 'Бонусы пользователей'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from .models import User, Board, Product, Stock, Story, CartItem, UserBonus, Store
from .forms import UserCreationForm, UserChangeForm


class ImagePreviewMixin:
    def image_preview(self, obj):
        if hasattr(obj, 'image') and obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height:100px; max-width:100px;" />')
        return 'Нет изображения'
    image_preview.short_description = 'Изображение'


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ('phone', 'first_name', 'last_name', 'is_phone_verified', 'is_staff', 'is_active')
    list_filter = ('is_phone_verified', 'is_staff', 'is_active')
    search_fields = ('phone', 'first_name', 'last_name')
    ordering = ('phone',)

    fieldsets = (
        (None, {'fields': ('phone', 'password', 'code')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name')}),
        ('Права доступа', {'fields': ('is_phone_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('name', 'price', 'barcode', 'discount', 'image_preview', 'is_featured')
    search_fields = ('name', 'barcode')
    list_filter = ('is_featured',)
    readonly_fields = ('image_preview',)
    fields = ('name', 'price', 'discount', 'barcode', 'label', 'image', 'image_preview', 'is_featured', 'store', 'created_at', 'updated_at')
    readonly_fields += ('created_at', 'updated_at')


@admin.register(Stock)
class StockAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('title', 'image', 'image_preview', 'created_at', 'updated_at')


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'created_at')
    list_filter = ('product',)
    search_fields = ('user__phone', 'product__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserBonus)
class UserBonusAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bonuses', 'created_at')
    search_fields = ('user__phone', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

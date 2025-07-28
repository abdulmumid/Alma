from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm  
from django.utils.safestring import mark_safe

def image_preview(obj):
    if hasattr(obj, 'image') and obj.image:
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />')
    return 'Нет изображения'
image_preview.short_description = 'Изображение'


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    icon_name  = "clipboard"
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ('phone', 'first_name', 'last_name', 'is_phone_verified', 'is_staff')
    list_filter = ('is_phone_verified', 'is_staff')
    search_fields = ('phone', 'first_name', 'last_name')
    ordering = ('phone',)

    fieldsets = (
        (None, {'fields': ('phone', 'password', 'code')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name')}),
        ('Права доступа', {'fields': ('is_phone_verified', 'is_active', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'first_name', 'last_name', 'password1', 'password2')}
        ),
    )


admin.site.register(User, CustomUserAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'barcode', 'discount', 'image_preview', 'is_featured')
    search_fields = ('name', 'barcode')
    readonly_fields = ('image_preview',)
    list_filter = ('is_featured',)
    fields = ('name', 'price', 'discount', 'barcode', 'label', 'image', 'image_preview', 'is_featured')


    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />')
        return "Нет изображения"

    image_preview.short_description = 'Изображение'
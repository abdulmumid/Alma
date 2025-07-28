from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserCreationForm(forms.ModelForm):
    """Форма для создания пользователя в админке"""
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Форма для изменения пользователя в админке"""
    password = ReadOnlyPasswordHashField(label="Пароль",
        help_text=("Пароль не отображается, но вы можете изменить его через форму 'Изменить пароль'."))

    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name', 'password', 'is_phone_verified', 'is_active', 'is_staff')

    def clean_password(self):
        # Возвращаем первоначальное значение пароля, независимо от входных данных формы.
        return self.initial["password"]

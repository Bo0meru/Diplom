from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        help_text="Пароль должен содержать минимум 8 символов, включая заглавные, строчные буквы, цифры и специальные символы."
    )
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        errors = []

        if len(password) < 8:
            errors.append("Пароль должен быть минимум 8 символов.")
        if not re.search(r'[A-Z]', password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву.")
        if not re.search(r'[a-z]', password):
            errors.append("Пароль должен содержать хотя бы одну строчную букву.")
        if not re.search(r'\d', password):
            errors.append("Пароль должен содержать хотя бы одну цифру.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            errors.append("Пароль должен содержать хотя бы один специальный символ.")

        if errors:
            raise ValidationError(errors)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Устанавливаем хэшированный пароль
        if commit:
            user.save()
        return user

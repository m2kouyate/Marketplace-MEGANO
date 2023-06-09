import re
from django.core.exceptions import ValidationError
from app_merch.models import Image
from django import forms
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm, UserChangeForm,
                                       UserCreationForm)
from django.contrib.auth.models import User
from django.forms.widgets import FileInput
from .models import Profile


class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "ФИО"}),
    )
    phone_number = forms.CharField(
        max_length=50,
        required=True,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Телефон"}),
    )
    address = forms.CharField(
        max_length=255,
        required=True,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Адрес"}),
    )
    avatar = forms.FileField(widget=FileInput(attrs={'hidden': '1'}), required=False, label="Аватар")

    password1 = forms.CharField(
        label="",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Пароль",
                "minlength": 8,
            }
        ),
        help_text="Пароль должен содержать не менее 8 символов и быть сложным",
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Подтверждение пароля",
                "minlength": 8,
            }
        ),
        help_text="Введите пароль еще раз для подтверждения",
    )
    username = forms.CharField(
        max_length=50,
        required=True,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Логин"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "full_name",
            "phone_number",
            "address",
            "avatar",
        ]
        labels = {
            "username": "Имя пользователя",
            "email": "",
        }
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254, required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '********'}), required=True, label=""
    )

    class Meta:
        model = User
        fields = ["username", "password"]
        labels = {
            "username": "Имя пользователя",
            "password": "Пароль",
        }


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254, required=True, label="Email")

    class Meta:
        model = User
        fields = ["email"]
        labels = {
            "email": "Email",
        }


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="Новый пароль"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="Подтверждение нового пароля"
    )

    class Meta:
        model = User
        fields = ["new_password1", "new_password2"]
        labels = {
            "new_password1": "Новый пароль",
            "new_password2": "Подтверждение нового пароля",
        }


class UserDataUpdateForm(SetPasswordForm):
    avatar = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "Profile-file form-input",
                "id": "avatar",
                "name": "avatar",
                "data-validate": "onlyImgAvatar",
            }
        )
    )
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
                attrs={
                    "class": "form-input",
                    "id": "name",
                    "name": "name",
                    "data-validate": "require",
                }
            )
    )
    phone = forms.CharField(
        widget=forms.TextInput(
                attrs={"class": "form-input", "id": "phone", "name": "phone", 'placeholder': '+7 (___) ___-____'}
            ),
    )
    mail = forms.EmailField(
        widget=forms.TextInput(
                attrs={
                    "class": "form-input",
                    "id": "mail",
                    "name": "mail",
                    "data-validate": "require",
                }
            )
    )
    new_password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "id": "new_password1",
                "name": "new_password1",
                "placeholder": "Тут можно изменить пароль",
            }
        ),
        strip=False,
    )
    new_password2 = forms.CharField(
        required=False,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "id": "new_password2",
                "name": "new_password2",
                "placeholder": "Введите пароль повторно",
            }
        ),
    )

    def clean_avatar(self):
        file = self.cleaned_data.get("avatar", False)
        if file:
            if file.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Размер файла не должен превышать 2 МБ")
            return file
        return

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not re.findall(r'^(\+7\s?\(\d{3}\)\s?\d{3}-\d{4})$', phone):
            raise ValidationError("Номер телефона должен иметь формат +7 (000) 000-0000")
        return re.sub(r'\D', '', phone)[1:]

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            return super(UserDataUpdateForm, self).clean_new_password2()

    def __init__(self, user, *args, **kwargs):
        super(UserDataUpdateForm, self).__init__(user, *args, **kwargs)
        self.fields["full_name"].initial = self.user.profile.full_name
        phone_number = self.user.profile.phone_number
        self.fields["phone"].initial = f"+7 ({phone_number[:3]}) {phone_number[3:6]}-{phone_number[6:]}"
        self.fields["mail"].initial = self.user.email

    def save(self, *args, commit=True, **kwargs):
        user = kwargs.get("request").user
        profile = user.profile
        avatar = profile.avatar
        user.email = self.cleaned_data["mail"]
        user.save()
        if self.cleaned_data["avatar"]:
            avatar.file = self.cleaned_data["avatar"]
            avatar.title = f"{user.username}'s profile image: {self.cleaned_data['avatar'].name}"
            avatar.save()
            profile.avatar = avatar
        profile.full_name = self.cleaned_data["full_name"]
        profile.phone_number = self.cleaned_data["phone"]
        profile.save()
        user = super(UserDataUpdateForm, self).save(commit=True)
        auth_login(kwargs.get("request"), user)

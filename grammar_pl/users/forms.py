from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    avatar = forms.ImageField(required=False, widget=forms.FileInput)
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('email', 'about', 'birth', 'first_name', 'last_name', 'avatar')
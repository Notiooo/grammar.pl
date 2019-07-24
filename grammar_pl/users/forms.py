from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    error_css_class = "uk-form-danger"
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):
    error_css_class = "uk-form-danger"
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'birth')
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "country",
            "avatar",
        )

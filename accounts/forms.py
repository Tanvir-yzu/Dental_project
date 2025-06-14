from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

class ResetPasswordForm(forms.Form):
    otp = forms.CharField(max_length=6)
    new_password = forms.CharField(widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'address',
            'current_occupation', 'gender', 'age', 'educational_institute',
            'profile_photo'
        ]
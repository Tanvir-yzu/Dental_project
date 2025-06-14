from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import EmailOTP
from .utils import send_otp_email
from .forms import RegisterForm, LoginForm, OTPForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm

User = get_user_model()

class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.role = 'student'
            user.save()
            send_otp_email(user)
            return redirect('verify_email', user_id=user.id)
        return render(request, 'accounts/register.html', {'form': form})

class VerifyEmailView(View):
    def get(self, request, user_id):
        form = OTPForm()
        return render(request, 'accounts/verify_email.html', {'form': form})

    def post(self, request, user_id):
        form = OTPForm(request.POST)
        user = User.objects.get(id=user_id)
        if form.is_valid():
            otp_obj = EmailOTP.objects.filter(user=user, code=form.cleaned_data['otp']).last()
            if otp_obj and otp_obj.is_valid():
                user.is_email_verified = True
                user.save()
                return redirect('login')
            else:
                return render(request, 'accounts/verify_email.html', {'form': form, 'error': 'Invalid OTP'})
        return render(request, 'accounts/verify.html', {'form': form, 'error': 'Invalid OTP'})

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            # Check if user exists but email is not verified
            if user and not user.is_email_verified:
                # Send a new OTP for verification
                send_otp_email(user)
                return redirect('verify_email', user_id=user.id)
            elif user and user.is_email_verified:
                login(request, user)
                return redirect('profile')
            else:
                # Invalid credentials
                return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid credentials'})
        return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid form data'})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class ForgotPasswordView(View):
    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, 'accounts/forgot_password.html', {'form': form})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                send_otp_email(user)
                return redirect('reset_password', user_id=user.id)
        return render(request, 'accounts/forgot_password.html', {'form': form, 'error': 'User not found'})

class ResetPasswordView(View):
    def get(self, request, user_id):
        form = ResetPasswordForm()
        return render(request, 'accounts/reset_password.html', {'form': form})

    def post(self, request, user_id):
        form = ResetPasswordForm(request.POST)
        user = User.objects.get(id=user_id)
        if form.is_valid():
            otp_obj = EmailOTP.objects.filter(user=user, code=form.cleaned_data['otp']).last()
            if otp_obj and otp_obj.is_valid():
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                return redirect('login')
        return render(request, 'accounts/reset_password.html', {'form': form, 'error': 'Invalid OTP'})

class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, 'accounts/profile_update.html', {'form': form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'accounts/profile_update.html', {'form': form, 'error': 'Invalid form data'})

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/profile.html')

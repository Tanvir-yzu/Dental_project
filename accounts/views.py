from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import EmailOTP
from .utils import send_otp_email, get_client_ip
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
            messages.success(request, 'Registration successful! Please verify your email.')
            return redirect('verify_email', user_id=user.id)
        return render(request, 'accounts/register.html', {'form': form})

class VerifyEmailView(View):
    def get(self, request, user_id):
        # Make sure user exists
        user = get_object_or_404(User, id=user_id)
        form = OTPForm()
        return render(request, 'accounts/verify_email.html', {'form': form})

    def post(self, request, user_id):
        form = OTPForm(request.POST)
        # Make sure user exists
        user = get_object_or_404(User, id=user_id)
        if form.is_valid():
            otp_obj = EmailOTP.objects.filter(user=user, code=form.cleaned_data['otp']).last()
            if otp_obj and otp_obj.is_valid():
                user.is_email_verified = True
                otp_obj.is_used = True  # Mark OTP as used
                otp_obj.save()
                user.save()
                messages.success(request, 'Email verified successfully! You can now login.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid or expired OTP')
                return render(request, 'accounts/verify_email.html', {'form': form, 'error': 'Invalid or expired OTP'})
        return render(request, 'accounts/verify_email.html', {'form': form, 'error': 'Invalid OTP'})

class LoginView(View):
    def get(self, request):
        # If user is already logged in, redirect to profile
        if request.user.is_authenticated:
            return redirect('profile')
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()  # Normalize email
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            # Check if user exists but email is not verified
            if user and not user.is_email_verified:
                # Send a new OTP for verification
                send_otp_email(user)
                messages.info(request, 'Your email is not verified. A new verification code has been sent.')
                return redirect('verify_email', user_id=user.id)
            elif user and user.is_email_verified:
                # Log out from previous sessions if any
                user.logout_previous_session()
                
                # Login the user
                login(request, user)
                
                # Update IP address and session key
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0].strip()
                else:
                    ip = request.META.get('REMOTE_ADDR')
                
                user.last_login_ip = ip
                user.session_key = request.session.session_key
                user.save()
                
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('profile')
            else:
                # Invalid credentials
                messages.error(request, 'Invalid credentials')
                return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid credentials'})
        return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid form data'})

class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # Clear session key before logout
            request.user.session_key = None
            request.user.save()
            logout(request)
            messages.success(request, 'You have been logged out successfully')
        return redirect('login')

class ForgotPasswordView(View):
    def get(self, request):
        # If user is already logged in, redirect to profile
        if request.user.is_authenticated:
            return redirect('profile')
        form = ForgotPasswordForm()
        return render(request, 'accounts/forgot_password.html', {'form': form})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()  # Normalize email
            user = User.objects.filter(email=email).first()
            if user:
                send_otp_email(user)
                messages.success(request, 'Password reset code has been sent to your email')
                return redirect('reset_password', user_id=user.id)
            else:
                messages.error(request, 'No account found with this email address')
        return render(request, 'accounts/forgot_password.html', {'form': form, 'error': 'User not found'})

class ResetPasswordView(View):
    def get(self, request, user_id):
        # Make sure user exists
        user = get_object_or_404(User, id=user_id)
        form = ResetPasswordForm()
        return render(request, 'accounts/reset_password.html', {'form': form})

    def post(self, request, user_id):
        form = ResetPasswordForm(request.POST)
        # Make sure user exists
        user = get_object_or_404(User, id=user_id)
        if form.is_valid():
            otp_obj = EmailOTP.objects.filter(user=user, code=form.cleaned_data['otp']).last()
            if otp_obj and otp_obj.is_valid():
                user.set_password(form.cleaned_data['new_password'])
                otp_obj.is_used = True  # Mark OTP as used
                otp_obj.save()
                user.save()
                messages.success(request, 'Password has been reset successfully. You can now login with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid or expired OTP')
        return render(request, 'accounts/reset_password.html', {'form': form, 'error': 'Invalid OTP'})

class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, 'accounts/profile_update.html', {'form': form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        return render(request, 'accounts/profile_update.html', {'form': form, 'error': 'Invalid form data'})

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/profile.html')
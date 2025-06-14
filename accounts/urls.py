from django.urls import path
from .views import RegisterView, VerifyEmailView, LoginView, LogoutView, ForgotPasswordView, ResetPasswordView, ProfileUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<int:user_id>/', VerifyEmailView.as_view(), name='verify_email'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<int:user_id>/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
]
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
from .models import EmailOTP

def send_otp_email(user):
    code = str(random.randint(100000, 999999))
    EmailOTP.objects.create(user=user, code=code)
    
    # Prepare HTML content
    html_message = render_to_string(
        'email/otp_email.html',
        {
            'user': user,
            'code': code,
            'site_name': 'Dental Training Academy'
        }
    )
    
    # Strip HTML for plain text version
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='Your Verification Code - Dental Training Academy',
        message=plain_message,
        html_message=html_message,
        from_email='Dental Training Academy <yourgmail@gmail.com>',
        recipient_list=[user.email],
        fail_silently=False,
    )
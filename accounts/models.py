from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.sessions.models import Session
ROLE_CHOICES = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('admin', 'Admin'),
)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

class CustomUser(AbstractUser):
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_email_verified = models.BooleanField(default=False)
    current_occupation = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(150)],
        blank=True, 
        null=True
    )
    educational_institute = models.CharField(max_length=255, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

    def generate_student_id(self):
        year = timezone.now().year
        # Try to generate a unique ID with retries
        max_attempts = 10
        for attempt in range(max_attempts):
            # Get the count of students created in the current year
            count = CustomUser.objects.filter(
                student_id__startswith=f'DTA-{year}',
                role='student'
            ).count()
            # Generate 6-digit sequential number
            sequence = str(count + 1).zfill(6)
            student_id = f'DTA-{year}-{sequence}'
            
            # Check if this ID already exists
            if not CustomUser.objects.filter(student_id=student_id).exists():
                return student_id
        
        # If we've exhausted all attempts, create a truly unique ID using timestamp
        timestamp = int(timezone.now().timestamp())
        sequence = str(timestamp)[-6:].zfill(6)  # Use last 6 digits of timestamp
        return f'DTA-{year}-{sequence}'

    def save(self, *args, **kwargs):
        if self.email:  # Check if email exists before lowercasing
            self.email = self.email.lower()
        if self.role == 'student' and not self.student_id:
            self.student_id = self.generate_student_id()
        super().save(*args, **kwargs)
        
    def logout_previous_session(self):
        if self.session_key:
            try:
                Session.objects.get(session_key=self.session_key).delete()
            except Session.DoesNotExist:
                pass
            self.session_key = None
            self.save()

class EmailOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email OTP'
        verbose_name_plural = 'Email OTPs'
        ordering = ['-created_at']

    def is_valid(self):
        if self.is_used:
            return False
        # Use timezone.now() consistently for timezone-aware comparison
        expiry_time = self.created_at + timedelta(minutes=5)
        return timezone.now() <= expiry_time

    def __str__(self):
        return f"OTP for {self.user.email}"
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, EmailOTP

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email', 'first_name', 'last_name', 'role', 
        'is_email_verified', 'is_active', 'profile_image_preview',
        'last_login_ip', 'session_key'
    )
    list_filter = ('role', 'is_email_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'student_id', 'last_login_ip')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'phone_number', 'address',
                'current_occupation', 'gender', 'age',
                'educational_institute', 'student_id', 'profile_photo', 'profile_image_preview'
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Verification & Role', {'fields': ('is_email_verified', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Session Info', {'fields': ('last_login_ip', 'session_key')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email','first_name', 'last_name', 'phone_number', 
                'password1', 'password2', 'address', 'current_occupation', 
                'gender', 'age', 'educational_institute', 'role'
            ),
        }),
    )

    readonly_fields = ('student_id', 'profile_image_preview', 'last_login_ip', 'session_key')

    def profile_image_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 50%;" />', obj.profile_photo.url)
        return "(No image)"
    profile_image_preview.short_description = 'Profile Photo'

class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(EmailOTP, EmailOTPAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, EmailOTP

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email', 'first_name', 'last_name', 'role', 
        'is_email_verified', 'is_active', 'profile_image_preview'
    )
    list_filter = ('role', 'is_email_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'student_id')
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
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2',
                'address', 'current_occupation', 'gender', 'age', 'educational_institute', 'role'
            ),
        }),
    )

    readonly_fields = ('student_id', 'profile_image_preview')

    def profile_image_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 50%;" />', obj.profile_photo.url)
        return "(No image)"
    profile_image_preview.short_description = 'Profile Photo'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(EmailOTP)

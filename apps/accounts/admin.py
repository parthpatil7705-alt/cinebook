from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'city', 'avatar', 'date_of_birth', 'total_bookings')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

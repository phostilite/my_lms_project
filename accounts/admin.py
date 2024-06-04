from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  

from .models import User, Learner, Instructor, Administrator

admin.site.register(Learner)
admin.site.register(Instructor)
admin.site.register(Administrator)

@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'gender', 'picture')}),  
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
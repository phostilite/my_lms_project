from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  

from .models import User, Learner, Instructor, Administrator, Supervisor, Facilitator

admin.site.register(Learner)
admin.site.register(Instructor)
admin.site.register(Administrator)
admin.site.register(Supervisor)
admin.site.register(Facilitator)

@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'gender', 'picture')}),  
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
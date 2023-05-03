from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UserInfo
# Register your models here.
@admin.register(UserInfo)
class UserAdmin(UserAdmin):
    list_display = ('username', 'realname', 'is_superuser')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Personal info', {'fields': ('realname', 'gender', 'age')}),
    )
    def has_add_permission(self, request): 
        if request.user.is_superuser:  
            return True  
        else:  
            return False
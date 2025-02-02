from django.contrib import admin

from .models import *

class CustomUserAdmin(admin.ModelAdmin):
    list_display =('id' , 'username'  , 'first_name','last_name')

    @admin.display(description="Name")
    def upper_case_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".upper()

# Register your models here.

admin.site.register(CustomUser , CustomUserAdmin)

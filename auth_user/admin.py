from django.contrib import admin

from auth_user.models import CustomUser

# Register your models here.
admin.site.register(CustomUser)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from cyberxclient.models import Users

admin.site.register(Users, UserAdmin)
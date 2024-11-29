# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import User , AnonymousUser ,OTP



admin.site.register(User)


admin.site.register(AnonymousUser)
admin.site.register(OTP)
# myapp/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone
from datetime import timedelta



class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    camera_id = models.CharField(max_length=255,null=True,blank=True)
    is_permission = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)







    def __str__(self):
        return self.email


class AnonymousUser(models.Model):

    camera_id = models.CharField(max_length=255)
    is_permission = models.BooleanField(default=True)


    def __str__(self):
        return self.camera_id
    


class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.email}"

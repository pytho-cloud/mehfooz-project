# myapp/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    camera_id = models.CharField(max_length=255,null=True,blank=True)
    is_permission = models.BooleanField(default=True)







    def __str__(self):
        return self.email


class AnonymousUser(models.Model):

    camera_id = models.CharField(max_length=255)
    is_permission = models.BooleanField(default=True)


    def __str__(self):
        return self.camera_id
    
    
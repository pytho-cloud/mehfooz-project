# myapp/serializers.py
from rest_framework import serializers
from .models import User
from .helper import *
from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import check_password ,make_password


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password.')

        # Manually hash the input password and compare it to the stored hashed password
        if user.password != password:
            raise serializers.ValidationError('Invalid email or password.')

        # Check if user is verified
        if not user.is_verified:
            raise serializers.ValidationError('User not verified. Please verify your email.')

        attrs['user'] = user  # Store the user for further processing
        return attrs



class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

 
   





class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()
  

    
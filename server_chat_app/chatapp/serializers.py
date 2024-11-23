# myapp/serializers.py
from rest_framework import serializers
from .models import User

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
            print("this is workin in serializer",user)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password.')

        # Manually hash the input password and compare it to the stored hashed password
        if user.password != password:
            print("this is workin in serializer",password)
            raise serializers.ValidationError('Invalid email or password.')

        attrs['user'] = user  # Store the user for further processing
        return attrs




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User(**validated_data)
        user.save()
        return user

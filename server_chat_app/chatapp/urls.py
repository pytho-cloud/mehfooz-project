# myapp/urls.py
from django.urls import path
from .views import LoginView, RegisterView ,OnlineUserView ,ForgetPasswordView ,VerifyOTPView ,AnonymousUserLogin ,UserBannedView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
       path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),  # Step 2
     path('online-user/', OnlineUserView.as_view(), name='online-user'),
      path('anonymous-user/', AnonymousUserLogin.as_view(), name='anonymous-user'),
       path('user-banned/', UserBannedView.as_view(), name='anonymous-user-banned'),

     path('forget-password/',ForgetPasswordView.as_view() ,name='forget-password')

]

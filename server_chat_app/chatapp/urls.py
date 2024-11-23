# myapp/urls.py
from django.urls import path
from .views import LoginView, RegisterView ,OnlineUserView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
     path('online-user/', OnlineUserView.as_view(), name='online-user'),

]

from django.urls import path
from auth_user.views import user_login, register

urlpatterns = [
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
]

app_name = 'auth_user'

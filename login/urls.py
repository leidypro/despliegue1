from django.urls import path
from login.views import *
from django.contrib.auth.views import LogoutView
app_name = 'login'
urlpatterns = [  
    path('', CreLoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(next_page='login:login'), name="logout"),
]
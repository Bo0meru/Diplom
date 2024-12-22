# accounts/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import login_register_view, profile
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', login_register_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', profile, name='profile'),

]
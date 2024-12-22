from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Убедитесь, что этот маршрут указывает на нужное представление
    path('about/', views.about, name='about')
]

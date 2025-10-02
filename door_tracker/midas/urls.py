from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('get_statistics', views.get_statistics, name='get_statistics'),
]

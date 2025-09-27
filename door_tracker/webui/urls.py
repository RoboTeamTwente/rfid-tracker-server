from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete_tag', views.delete_tag, name='delete_tag'),
    path('rename_tag', views.rename_tag, name='rename_tag'),
    path('fuel_guage', views.fuel_guage, name='fuel_guage'),
    path('healthcheck', views.healthcheck, name='healthcheck'),
    path('login', views.LogIn.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('user_statistics', views.user_statistics, name='user_statistics'),
    path('user_tags', views.user_tags, name='user_tags'),
    path('export_user', views.export_user_logs, name='export_user'),
    path('auto_checkout', views.auto_checkout, name='auto_checkout'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
]

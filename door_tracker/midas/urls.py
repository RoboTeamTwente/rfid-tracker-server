from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
)
from webui import views as old_views

from . import api, views

app_name = 'midas'
urlpatterns = [
    # API
    path('api/auth/', include('rest_framework.urls')),
    path('api/checkout', api.checkout, name='checkout'),
    path('api/healthcheck', api.healthcheck, name='healthcheck'),
    path('api/register_scan', api.register_scan, name='register_scan'),
    path(
        'api/',
        SpectacularRedocView.as_view(url_name='midas:schema'),
    ),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # views
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('login', views.LogIn.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('', views.index, name='index'),
    # old
    path('delete_tag', old_views.delete_tag, name='delete_tag'),
    path('export_user', old_views.export_user_logs, name='export_user'),
    path('fuel_guage', old_views.fuel_guage, name='fuel_guage'),
    path('healthcheck', old_views.healthcheck, name='healthcheck'),
    path('rename_tag', old_views.rename_tag, name='rename_tag'),
    path('sign_up', old_views.sign_up, name='sign_up'),
    path('user_statistics', old_views.user_statistics, name='user_statistics'),
    path('user_tags', old_views.user_tags, name='user_tags'),
]

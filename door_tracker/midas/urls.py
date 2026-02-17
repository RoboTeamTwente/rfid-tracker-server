from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
)

from . import api, views

app_name = 'midas'
urlpatterns = [
    # API
    path('api/auth/', include('rest_framework.urls')),
    path('api/checkout', api.checkout, name='checkout'),
    path('api/checkin', api.checkin, name='checkin'),
    path('api/healthcheck', api.healthcheck, name='healthcheck'),
    path('api/register_scan', api.register_scan, name='register_scan'),
    path('api/export/sessions', api.export_sessions_csv, name='export_user'),
    path(
        'api/',
        SpectacularRedocView.as_view(url_name='midas:schema'),
    ),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # views
    path('delete_tag', views.delete_tag, name='delete_tag'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('login', views.LogIn.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('rename_tag', views.rename_tag, name='rename_tag'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('user_statistics', views.user_statistics, name='user_statistics'),
    path('team_overview', views.team_overview, name='team_overview'),
    path('user_overview', views.user_overview, name='user_overview'),

    path('', views.index, name='index'),
]

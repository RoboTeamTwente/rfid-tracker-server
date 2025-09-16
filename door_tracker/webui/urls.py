from django.urls import path

from . import views

# add new url
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.LogIn.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('current_user_data', views.current_user_data, name='utable_data'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('user_statistics', views.user_statistics, name='user_statistics'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('export', views.export, name='export'),
    path('fuel_guage', views.fuel_guage, name='fuel_guage'),
    path(
        'create_pending_reg',
        views.create_pending_reg,
        name='create_pending_reg',
    ),
    path('user_tags', views.user_tags, name='user_tags'),
    path(
        'check_registration/<int:db_id>/',
        views.check_registration,
        name='check_registration',
    ),
]

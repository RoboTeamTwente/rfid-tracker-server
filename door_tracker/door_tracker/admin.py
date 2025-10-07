import secrets

from django.contrib import admin
from django.core.cache import cache
from django.http import JsonResponse
from django.urls import path, reverse

TOKEN_LIFETIME = 24 * 360  # How long until the link expires


def generate_register_link(request):
    token = secrets.token_urlsafe(16)
    cache.set(f'register_token_{token}', True, timeout=TOKEN_LIFETIME)
    relative_link = reverse('midas:sign_up', query={'token': token})
    link = request.build_absolute_uri(relative_link)
    return JsonResponse({'link': link})


class DoorTrackerAdminSite(admin.AdminSite):
    def get_urls(self):
        return [
            path(
                'make-registration-link/',
                self.admin_view(generate_register_link),
                name='make-registration-link',
            ),
        ] + super().get_urls()

    # stolen from AdminSite implementation, but without the sorting part
    # https://forum.djangoproject.com/t/reordering-list-of-models-in-django-admin/5300/9
    def get_app_list(self, request, app_label=None):
        return self._build_app_dict(request, app_label).values()

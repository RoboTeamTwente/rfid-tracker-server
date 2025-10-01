from django.contrib import admin
from django.contrib.admin import register

from .models import (
    Assignment,
    Checkin,
    Checkout,
    ClaimedTag,
    PendingTag,
    Quota,
    Scanner,
    Session,
    Subteam,
    SubteamMembership,
)


class SubteamMembershipInline(admin.TabularInline):
    model = SubteamMembership


class CheckinInline(admin.StackedInline):
    model = Checkin


class CheckoutInline(admin.StackedInline):
    model = Checkout


@register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['checkin__time', 'checkout__time', 'owner']
    inlines = [CheckinInline, CheckoutInline]

    def get_readonly_fields(self, request, obj=None):
        default = super().get_readonly_fields(request, obj)
        if obj is not None:  # when editing
            default = list(default) + ['owner']
        return default


@register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    inlines = [SubteamMembershipInline]
    list_display = ['starting_from', 'user__username', 'quota__name']


@register(ClaimedTag)
class ClaimedTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner__username']


@register(PendingTag)
class PendingTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner__username', 'scanner__name']


@register(Scanner)
class ScannerAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']


@register(Subteam)
class SubteamAdmin(admin.ModelAdmin):
    list_display = ['name']


@register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    list_display = ['name', 'hours']

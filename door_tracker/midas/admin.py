from django.contrib import admin
from django.contrib.admin import register

from .models import (
    Assignment,
    ClaimedTag,
    Log,
    PendingTag,
    Quota,
    Scanner,
    Session,
    Subteam,
    SubteamMembership,
)


class SubteamMembershipInline(admin.TabularInline):
    model = SubteamMembership


@register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['checkin__time', 'checkout__time', 'owner']


@register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['type', 'time', 'tag__name', 'tag__owner__username']


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

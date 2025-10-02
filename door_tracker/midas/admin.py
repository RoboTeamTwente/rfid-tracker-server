from django.contrib import admin
from django.urls import resolve

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
)


class LogInline(admin.StackedInline):
    radio_fields = {'type': admin.HORIZONTAL}

    # filters tags by session user
    # XXX: doesnt work when a new session is created
    def get_field_queryset(self, db, db_field, request):
        if db_field.name == 'tag':
            parent_id = resolve(request.path_info).kwargs.get('object_id')
            if parent_id:
                session = self.parent_model.objects.get(pk=parent_id)
                return ClaimedTag.objects.filter(owner=session.user)
        return super().get_field_queryset(db, db_field, request)


class CheckinInline(LogInline):
    model = Checkin


class CheckoutInline(LogInline):
    model = Checkout


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['checkin__time', 'checkout__time', 'user']
    inlines = [CheckinInline, CheckoutInline]
    autocomplete_fields = ['user']
    ordering = ['-checkin__time', '-checkout__time']

    def get_readonly_fields(self, request, obj=None):
        default = super().get_readonly_fields(request, obj)
        if obj is not None:  # when editing
            default = list(default) + ['user']
        return default


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['starting_from', 'user__username', 'quota__name']
    filter_horizontal = ['subteams']
    autocomplete_fields = ['user']
    ordering = ['-starting_from']


@admin.register(ClaimedTag)
class ClaimedTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner__last_name', 'owner__first_name']
    search_fields = ['name', 'owner__last_name', 'owner__first_name']
    autocomplete_fields = ['owner']
    ordering = ['owner__last_name', 'owner__first_name', 'name']

    def get_readonly_fields(self, request, obj=None):
        default = super().get_readonly_fields(request, obj)
        if obj is not None:  # when editing
            default = list(default) + ['owner', 'code']
        return default

    def has_add_permission(self, request):
        return False


@admin.register(PendingTag)
class PendingTagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'owner__last_name',
        'owner__first_name',
        'scanner__name',
    ]
    autocomplete_fields = ['owner']
    ordering = [
        'owner__last_name',
        'owner__first_name',
        'name',
    ]


@admin.register(Scanner)
class ScannerAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    readonly_fields = ['id']
    ordering = ['name']


@admin.register(Subteam)
class SubteamAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_editable = ['name']
    list_display_links = None
    ordering = ['name']


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    list_display = ['name', 'hours']
    list_editable = ['name', 'hours']
    list_display_links = None
    ordering = ['name']

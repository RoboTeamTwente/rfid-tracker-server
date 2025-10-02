from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import resolve
from django.utils import timezone

from .models import (
    Assignment,
    Checkin,
    Checkout,
    ClaimedTag,
    LogType,
    PendingTag,
    Quota,
    Scanner,
    Session,
    Subteam,
)


class SessionSubteamListFilter(admin.SimpleListFilter):
    title = 'subteam'
    parameter_name = 'subteam'

    def lookups(self, request, model_admin):
        return [(s.id, s) for s in Subteam.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        members = Assignment.objects.filter_effective().filter(subteam=self.value())
        return queryset.filter(user__in=members.values('person'))


class SessionUserListFilter(admin.SimpleListFilter):
    title = 'user'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        return [(u.id, u.get_full_name()) for u in User.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(user=self.value())


class SessionLogTypeListFilter(admin.SimpleListFilter):
    title = 'log type'
    parameter_name = 'log_type'

    def lookups(self, request, model_admin):
        return [
            ('tag', 'Physical Tag'),
            ('remote', 'Remote Tag'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'tag':
            return queryset.filter(
                Q(checkout__type=LogType.TAG) | Q(checkin__type=LogType.TAG)
            )
        elif self.value() == 'remote':
            return queryset.filter(
                Q(checkout__type=LogType.REMOTE) | Q(checkin__type=LogType.REMOTE)
            )
        return queryset


class AssignmentSubteamListFilter(admin.SimpleListFilter):
    title = 'subteam'
    parameter_name = 'subteam'

    def lookups(self, request, model_admin):
        return [(s.id, s) for s in Subteam.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        members = Assignment.objects.filter_effective().filter(subteam=self.value())
        return queryset.filter(user__in=members.values('person'))


class AssignmentUserListFilter(admin.SimpleListFilter):
    title = 'user'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        return [(u.id, u.get_full_name()) for u in User.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(user=self.value())


class AssignmentQuotaListFilter(admin.SimpleListFilter):
    title = 'quota'
    parameter_name = 'quota'

    def lookups(self, request, model_admin):
        return [(q.id, q.name) for q in Quota.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(quota=self.value())


class AssignementDateListFilter(admin.SimpleListFilter):
    title = 'assignement status'
    parameter_name = 'starting_from'

    def lookups(self, request, model_admin):
        return [
            ('current', 'Active'),
            ('past', 'Past'),
            ('future', 'Future'),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        today = timezone.now()
        if self.value() == 'current':
            first_current = (
                queryset.filter(starting_from__lte=today)
                .order_by('-starting_from')
                .first()
            )
            if first_current:
                return queryset.filter(pk=first_current.pk)
            return queryset.none()
        elif self.value() == 'past':
            first_current = (
                queryset.filter(starting_from__lte=today)
                .order_by('-starting_from')
                .first()
            )
            if first_current:
                return queryset.filter(starting_from__lt=first_current.starting_from)
            return queryset.none()
        elif self.value() == 'future':
            return queryset.filter(starting_from__date__gt=today)
        else:
            return queryset


class ClaimedTagListFilter(admin.SimpleListFilter):
    title = 'owner'
    parameter_name = 'owner'

    def lookups(self, request, model_admin):
        return [(u.id, u.get_full_name()) for u in User.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(owner=self.value())


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
    list_display = [
        'checkin__time',
        'checkout__time',
        'user__last_name',
        'user__first_name',
    ]
    search_fields = ['user__last_name', 'user__first_name']
    list_filter = [
        SessionUserListFilter,
        SessionSubteamListFilter,
        SessionLogTypeListFilter,
    ]
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
    list_display = [
        'starting_from',
        'user__last_name',
        'user__first_name',
        'quota__name',
        'get_subteams',
    ]
    search_fields = ['user__last_name', 'user__first_name']
    list_filter = [
        AssignmentUserListFilter,
        AssignmentSubteamListFilter,
        AssignmentQuotaListFilter,
        AssignementDateListFilter,
    ]
    filter_horizontal = ['subteams']
    autocomplete_fields = ['user']
    ordering = ['-starting_from']


@admin.register(ClaimedTag)
class ClaimedTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner__last_name', 'owner__first_name']
    search_fields = ['name', 'owner__last_name', 'owner__first_name']
    list_filter = [ClaimedTagListFilter]
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

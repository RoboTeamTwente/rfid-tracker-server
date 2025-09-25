# admin.py
import secrets
from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.utils import timezone

from .models import Job, Log, Membership, Scanner, Statistics, SubTeam, Tag

admin.site.site_header = 'RoboTeam'
TOKEN_LIFETIME = 24 * 360  # How long until the link expires


class LogSubteamListFilter(admin.SimpleListFilter):
    title = 'subteam'
    parameter_name = 'subteam'

    def lookups(self, request, model_admin):
        return [(s.id, s) for s in SubTeam.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        members = Membership.objects.filter_effective().filter(subteam=self.value())
        return queryset.filter(tag__owner__in=members.values('person'))


class LogPersonListFilter(admin.SimpleListFilter):
    title = 'person'
    parameter_name = 'person'

    def lookups(self, request, model_admin):
        return [(u.id, u.get_full_name()) for u in User.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(tag__owner=self.value())


class LogTagListFilter(admin.SimpleListFilter):
    title = 'remote checkout'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        return [
            ('remote_checkout', 'Remote Checkouts'),
            ('normal_logs', 'Normal Logs'),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == 'remote_checkout':
            remote_checkout_logs = Tag.objects.filter(name='WebUI')
            return queryset.filter(tag__in=remote_checkout_logs)
        elif self.value() == 'normal_logs':
            normal_logs = Tag.objects.exclude(name='WebUI')
            return queryset.filter(tag__in=normal_logs)
        else:
            return queryset


class LogLogEntryTypeListFilter(admin.SimpleListFilter):
    title = 'log entry type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return [
            ('checkin', 'Check-in'),
            ('checkout', 'Check-out'),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == 'checkin':
            return queryset.filter(type__in=[Log.LogEntryType.CHECKIN])
        elif self.value() == 'checkout':
            return queryset.filter(type__in=[Log.LogEntryType.CHECKOUT])
        else:
            return queryset


class StatisticsSubteamListFilter(admin.SimpleListFilter):
    title = 'subteam'
    parameter_name = 'subteam'

    def lookups(self, request, model_admin):
        return [(s.id, s) for s in SubTeam.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        members = Membership.objects.filter_effective().filter(subteam=self.value())
        return queryset.filter(person__in=members.values('person'))


class StatisticsPersonListFilter(admin.SimpleListFilter):
    title = 'person'
    parameter_name = 'person'

    def lookups(self, request, model_admin):
        return [(u.id, u.get_full_name()) for u in User.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(person=self.value())


class TagStatusListFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('claimed', 'Claimed'),
            ('pending_registration', 'Pending registration'),
            ('unauthorized', 'Unauthorized'),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(status=self.value())


class TagOwnerListFilter(admin.SimpleListFilter):
    title = 'owner'
    parameter_name = 'owner'

    def lookups(self, request, model_admin):
        return [(u.id, u.get_full_name()) for u in User.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(owner=self.value())


class MemershipSubteamListFilter(admin.SimpleListFilter):
    title = 'subteam'
    parameter_name = 'subteam'

    def lookups(self, request, model_admin):
        return [(s.id, s) for s in SubTeam.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(subteam=self.value())


class MemershipJobListFilter(admin.SimpleListFilter):
    title = 'job'
    parameter_name = 'job'

    def lookups(self, request, model_admin):
        return [(j.id, j.name) for j in Job.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(job=self.value())


class MembershipDateListFilter(admin.SimpleListFilter):
    title = 'membership status'
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


class MembershipPersonListFilter(admin.SimpleListFilter):
    title = 'person'
    parameter_name = 'person'

    def lookups(self, request, model_admin):
        return [(u.id, u.get_full_name()) for u in User.objects.all()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(person=self.value())


def export_selected_logs(modeladmin, request, queryset):
    ids = queryset.values_list('pk', flat=True)
    url = reverse('export', query={'ids': ids})
    return HttpResponseRedirect(url)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    actions = [export_selected_logs]
    list_display = ('time', 'type', 'person', 'scanner')
    list_filter = (
        LogTagListFilter,
        LogSubteamListFilter,
        LogPersonListFilter,
        LogLogEntryTypeListFilter,
    )
    ordering = ('-time',)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('starting_from', 'person', 'subteam', 'job')
    ordering = ('-starting_from',)
    list_filter = (
        MembershipDateListFilter,
        MemershipJobListFilter,
        MemershipSubteamListFilter,
        MembershipPersonListFilter,
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'status', 'tag_code')
    list_filter = (TagStatusListFilter, TagOwnerListFilter)


@admin.register(SubTeam)
class NamedAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota')


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = (
        'person',
        'date',
        'hours_day',
        'hours_week',
        'hours_month',
        'average_hours_week',
        'total_hours',
    )
    ordering = ('-date',)
    list_filter = (StatisticsSubteamListFilter, StatisticsPersonListFilter)


@admin.register(Scanner)
class ScannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    readonly_fields = ('id',)


# this ungodly hack disables alphabetical sorting of models
# https://forum.djangoproject.com/t/reordering-list-of-models-in-django-admin/5300/9


def get_app_list(self, request, app_label=None):
    return list(self._build_app_dict(request, app_label).values())


def generate_register_link(request):
    token = secrets.token_urlsafe(16)
    cache.set(f'register_token_{token}', True, timeout=TOKEN_LIFETIME)
    link = request.build_absolute_uri(reverse('sign_up', query={'token': token}))
    expires_at = (timezone.now() + timedelta(seconds=TOKEN_LIFETIME)).isoformat()
    return JsonResponse({'link': link, 'expires_at': expires_at})


# admin.py (at the bottom)
def get_urls(original_get_urls):
    def custom_get_urls(self):
        urls = original_get_urls(self)
        custom_urls = [
            path(
                'generate-register-link/',
                self.admin_view(generate_register_link),
                name='generate_register_link',
            ),
        ]
        return custom_urls + urls

    return custom_get_urls


admin.AdminSite.get_app_list = get_app_list

admin.AdminSite.get_urls = get_urls(admin.AdminSite.get_urls)

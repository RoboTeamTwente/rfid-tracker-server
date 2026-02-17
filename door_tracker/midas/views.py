from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional

import pytz
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import serializers

from . import statistics
from .forms import RegistrationForm
from .models import Assignment, ClaimedTag, PendingTag, Quota, Scanner, Session, Subteam
from .statistics import (
    get_average_week,
    get_minutes_this_month,
    get_minutes_this_week,
    get_minutes_today,
    get_sessions_time,
    get_total_minutes,
)

# from django.views.decorators.csrf import csrf_exempt
# from rest_framework import serializers
# from rest_framework.decorators import (
#     api_view,
# )
# # Import Custom Files
# from .forms import RegistrationForm
# # Import Custom Files
# from .forms import RegistrationForm
# Create your views here.

# from .utils import logs_to_csv

AMSTERDAM_TZ = pytz.timezone('Europe/Amsterdam')


# Explicitly define Amsterdam Timezone
AMSTERDAM_TZ = pytz.timezone('Europe/Amsterdam')


def user_statistics(request):
    # 1. Get "Now" in Amsterdam Time
    utc_now = timezone.now()
    current_day = utc_now.astimezone(AMSTERDAM_TZ)

    # 2. Get Current Assignment
    latest_assignment = (
        Assignment.objects.filter_current().filter(user=request.user).first()
    )

    if latest_assignment:
        subteams = latest_assignment.subteams.all()
        subteam_name = (
            ', '.join([s.name for s in subteams]) if subteams else 'No Subteam'
        )
        # Get the raw weekly hours (e.g., 36)
        weekly_quota_hours = (
            latest_assignment.quota.hours if latest_assignment.quota else 0
        )
    else:
        subteam_name = 'You are alone Comrade'
        weekly_quota_hours = 0

    # 3. Get Worked Minutes
    total_minutes_day = get_minutes_today(request.user, current_day)
    total_minutes_week = get_minutes_this_week(request.user, current_day)
    total_minutes_month = get_minutes_this_month(request.user, current_day)
    total_minutes_all = get_total_minutes(request.user, current_day)
    average_minutes_week = get_average_week(request.user, current_day)

    weekly_hours_target = weekly_quota_hours

    start_of_month = current_day.replace(day=1)
    if current_day.month == 12:
        next_month = current_day.replace(year=current_day.year + 1, month=1, day=1)
    else:
        next_month = current_day.replace(month=current_day.month + 1, day=1)

    days_in_month = (next_month - start_of_month).days

    # (Days in Month / 7 days per week) * Weekly Hours
    monthly_hours_target = (days_in_month / 7.0) * weekly_quota_hours

    quota_week_met = (total_minutes_week / 60) >= weekly_hours_target
    quota_month_met = (total_minutes_month / 60) >= monthly_hours_target

    def format_time(minutes):
        minutes = int(minutes)
        hours = minutes // 60
        mins = minutes % 60
        s = f'{hours}h'
        if mins:
            s += f' {mins}m'
        return s

    return render(
        request,
        'midas/user_statistics.html',
        {
            # user info
            'user_name': request.user.get_full_name(),
            'user_role': subteam_name,
            'user_status': user_status(request),
            
            # totals (Work done) - FORMATTED FOR HTML DISPLAY
            'total_hours_day': format_time(total_minutes_day),
            'total_hours_week': format_time(total_minutes_week),
            'total_hours_month': format_time(total_minutes_month),
            'total_hours_all': format_time(total_minutes_all),
            'average_hours_week': format_time(average_minutes_week),
            
            # targets (Goals) - FORMATTED FOR HTML DISPLAY
            'quota_hours_week': format_time(weekly_hours_target * 60),
            'quota_hours_month': format_time(monthly_hours_target * 60),
            
            # quotas (Status)
            'quota_week_met': 'MET' if quota_week_met else 'UNMET',
            'quota_month_met': 'MET' if quota_month_met else 'UNMET',
            
            # js values - RAW NUMBERS FOR ECHARTS CALCULATION
            'script_data': {
                'total_hours_week': total_minutes_week,
                'quota_hours_week': weekly_hours_target * 60,
                'total_hours_month': total_minutes_month,
                'quota_hours_month': monthly_hours_target * 60,
            },
        },
    )

def team_overview(request):
    utc_now = timezone.now()
    current_day = utc_now.astimezone(AMSTERDAM_TZ)

    # 1. Date Range Handling
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str and end_date_str:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
    else:
        end_date = current_day.date()
        start_date = end_date - timedelta(days=6)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Create aware boundaries for get_sessions_time
    start_dt = AMSTERDAM_TZ.localize(datetime.combine(start_date, time.min))
    end_dt = AMSTERDAM_TZ.localize(datetime.combine(end_date + timedelta(days=1), time.min)) - timedelta(microseconds=1)

    # 2. Subteam Handling
    all_subteams = Subteam.objects.all()
    selected_id = request.GET.get('subteam_id')

    if selected_id:
        current_subteam = get_object_or_404(Subteam, id=selected_id)
    else:
        user_assignment = Assignment.objects.filter_current().filter(user=request.user).first()
        if user_assignment and user_assignment.subteams.exists():
            current_subteam = user_assignment.subteams.first()
        else:
            current_subteam = all_subteams.first()

    # 3. Data Extraction
    members = (
        Assignment.objects.filter_current()
        .filter(subteams=current_subteam)
        .select_related('user')
    )

    chart_labels = []
    chart_data = []
    total_hours_float = 0.0

    for assignment in members:
        user_obj = assignment.user
        
        # Calculate minutes spanning exact date range
        minutes = get_sessions_time(user_obj, start_dt, end_dt)
        hours = round(minutes / 60.0, 2)

        chart_labels.append(user_obj.get_full_name() or user_obj.username)
        chart_data.append(hours)
        total_hours_float += hours

    context = {
        'all_subteams': all_subteams,
        'current_subteam': current_subteam,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'summary': {
            'total_hours': round(total_hours_float, 2),
            'member_count': len(chart_labels),
            'avg_hours': round(total_hours_float / len(chart_labels), 1) if chart_labels else 0,
        },
        'page_data': {
            'meta': {
                'subteam_name': current_subteam.name if current_subteam else 'No Team',
            },
            'chart': {'labels': chart_labels, 'data': chart_data},
        },
    }

    return render(request, 'midas/team_overview.html', context)

def user_overview(request):
    utc_now = timezone.now()
    current_day = utc_now.astimezone(AMSTERDAM_TZ)

    # 1. Handle Date Range Selection
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str and end_date_str:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
    else:
        end_date = current_day.date()
        start_date = end_date - timedelta(days=6)

    # Enforce chronological order
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Cap maximum range to prevent excessive DB queries (e.g., 90 days)
    if (end_date - start_date).days > 90:
        start_date = end_date - timedelta(days=90)

    # 2. Handle User Selection
    all_users = User.objects.all().order_by('username')
    selected_id = request.GET.get('user_id')

    if selected_id:
        current_user = get_object_or_404(User, id=selected_id)
    else:
        current_user = request.user

    # 3. Standard Metrics
    minutes_today = get_minutes_today(current_user, current_day)
    minutes_week = get_minutes_this_week(current_user, current_day)
    minutes_month = get_minutes_this_month(current_user, current_day)

    def format_time(minutes):
        hours = int(minutes) // 60
        mins = int(minutes) % 60
        return f"{hours}h {mins}m" if mins else f"{hours}h"

    # 4. Generate Custom Range Chart Data
    chart_labels = []
    chart_data = []
    range_total_minutes = 0

    current_iter_date = start_date
    while current_iter_date <= end_date:
        day_minutes = get_minutes_today(current_user, current_iter_date)
        
        chart_labels.append(current_iter_date.strftime('%b %d'))
        chart_data.append(round(day_minutes / 60.0, 2))
        range_total_minutes += day_minutes
        
        current_iter_date += timedelta(days=1)

    latest_assignment = (
        Assignment.objects.filter_current().filter(user=current_user).first()
    )

    weekly_quota_hours = (
            latest_assignment.quota.hours if latest_assignment.quota else 0
        )
    weekly_quota_met = minutes_week / 60.0 >= weekly_quota_hours

    context = {
        'all_users': all_users,
        'current_user': current_user,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'summary': {
            'today': format_time(minutes_today),
            'week': format_time(minutes_week),
            'month': format_time(minutes_month),
            'range_total': format_time(range_total_minutes),
        },
        'page_data': {
            'meta': {
                'weekly_quota_met': 'MET' if weekly_quota_met else 'UNMET',
                'username': current_user.get_full_name() or current_user.username,
                'range_label': f"Hours Worked ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})",
            },
            'chart': {
                'labels': chart_labels,
                'data': chart_data
            }
        },
    }

    return render(request, 'midas/user_overview.html', context)


# TODO: Refactor for Midas
class LogIn(LoginView):
    template_name = 'midas/login.html'
    next_page = reverse_lazy('midas:index')

    def form_valid(self, form):
        user_name = form.get_user().get_full_name()
        messages.success(self.request, f'Welcome, comrade {user_name}')
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out')
    return redirect('midas:login')


@login_not_required
def sign_up(request):
    token = request.GET.get('token')

    # Check if token exists in cache
    if not token or not cache.get(f'register_token_{token}'):
        return HttpResponseForbidden('Invalid or expired registration link.')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('midas:login')  # replace with your login URL
    else:
        form = RegistrationForm()

    return render(request, 'midas/sign_up.html', {'form': form})


def is_checked_in(request):
    return Session.objects.filter(user=request.user, checkout__isnull=True).exists()


def user_status(request):
    return 'CHECKED-IN' if is_checked_in(request) else 'CHECKED-OUT'


def index(request):
    sessions = (
        Session.objects.filter(user=request.user)
        .select_related('checkin', 'checkout')
        .order_by('-checkin__time', '-checkout__time')
        .values(
            'id',
            'checkin__time',
            'checkin__type',
            'checkout__time',
            'checkout__type',
            'checkin__tag__name',
            'checkout__tag__name',
        )
    )
    return render(
        request,
        'midas/index.html',
        {
            'sessions': list(sessions),
            'user_status': user_status(request),
        },
    )


class AddTagSerializer(serializers.Serializer):
    tag_name = serializers.CharField()


class ScanTagSerializer(serializers.Serializer):
    tag = serializers.IntegerField()


def user_profile(request):
    modal_name = request.GET.get('modal')
    tag_param = request.GET.get('tag')

    # Base data
    pending_tags = PendingTag.objects.filter(owner=request.user).values('id', 'name')
    claimed_tags = ClaimedTag.objects.filter(owner=request.user).values('code', 'name')
    assignment = (
        Assignment.objects.filter_current()
        .filter(user=request.user)
        .select_related('quota')
        .prefetch_related('subteams')
        .first()
    )

    # Needed for Edit Profile
    subteams = Subteam.objects.all()
    quotas = Quota.objects.all()

    # Add Tag: User just entered a tag name
    if request.POST.get('action') == 'add_tag':
        serializer = AddTagSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)

        tag_name = serializer.validated_data['tag_name']

        # Create a new PendingTag entry (if one doesn't already exist)
        scanner = Scanner.objects.filter(pending_tag__isnull=True).first()
        if not scanner:
            messages.error(
                request,
                'Someone else is registering a tag right now. Please try again later.',
            )
            return redirect('midas:user_profile')

        pending_tag = PendingTag.objects.create(
            scanner=scanner,
            owner=request.user,
            name=tag_name,
        )

        # Redirect to "waiting for scan" modal
        return redirect(
            reverse_lazy(
                'midas:user_profile',
                query={'modal': 'tag_scan', 'tag': pending_tag.id},
            )
        )

    # Polling modal: check if tag was claimed
    if modal_name == 'tag_scan' and tag_param:
        # has this tag been moved to ClaimedTag by the scanner?
        pending_tag_exists = PendingTag.objects.filter(id=tag_param).exists()
        if not pending_tag_exists:
            # pending tag disappeared → must have been claimed
            return HttpResponse(
                headers={'HX-Redirect': reverse_lazy('midas:user_profile')}
            )

    # Render profile page normally ---
    return render(
        request,
        'midas/user_profile.html',
        {
            'user_status': user_status(request),
            'assignment': assignment,
            'subteams': subteams,
            'quotas': quotas,
            'modal_name': modal_name,
            'claimed_tags': list(claimed_tags),
            'pending_tags': list(pending_tags),
        },
    )


def get_all_statistics(request):
    date = timezone.now().date()
    all_stats = []

    # Extract filters from request (GET params or POST data)
    user_id = request.GET.get('user')
    subteam_name = request.GET.get('subteam')
    quota_name = request.GET.get('quota')
    date = request.GET.get('date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    users = User.objects.all()
    dates = []

    # Apply filters if provided
    if user_id:
        users = users.filter(id=user_id)
    if subteam_name:
        users = users.filter(assignments__subteams__name=subteam_name)
    if quota_name:
        users = users.filter(assignments__quota__name=quota_name)
    users = users.distinct()

    # Handle date filters
    if date:
        try:
            date = datetime.strptime(date, '%d-%m-%Y').date()
            dates = [date]
        except ValueError:
            return HttpResponse('Invalid date format. Use DD-MM-YYYY.', status=400)
    elif start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
            end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
            if start_date > end_date:
                return HttpResponse('Start date must be before end date.', status=400)
            delta = (end_date - start_date).days
            dates = [start_date + timedelta(days=i) for i in range(delta + 1)]
        except ValueError:
            return HttpResponse('Invalid date format. Use DD-MM-YYYY.', status=400)
    else:
        dates = {timezone.now().date()}

    # Loop through all users and get their statistics
    for date in dates:
        for user in users:
            # Get current assignment
            assignment = (
                Assignment.objects.filter(user=user, starting_from__lte=date)
                .order_by('-starting_from')
                .first()
            )  # returns None if no assignment
            subteams = assignment.subteam_names() if assignment else 'No subteam'
            quota = assignment.quota.hours if assignment else 'No quota'
            user_stats = {
                'name': user.first_name + ' ' + user.last_name,
                'subteam': subteams,
                'quota': quota,
                'date': date,
                'minutes_today': statistics.get_minutes_today(user, date),
                'minutes_this_week': statistics.get_minutes_this_week(user, date),
                'minutes_this_month': statistics.get_minutes_this_month(user, date),
                'total_minutes': statistics.get_total_minutes(user, date),
                'average_week': statistics.get_average_week(user, date),
            }
            all_stats.append(user_stats)

    return all_stats


@dataclass
class EditMembershipRequest:
    first_name: str
    last_name: str
    username: str
    subteams: Optional[list[int]]
    quota: Optional[int]


class EditMembershipRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    subteams = serializers.ListField(child=serializers.IntegerField(), required=False)
    quota = serializers.IntegerField(required=False)

    def create(self, validated_data):
        return EditMembershipRequest(**validated_data)


def edit_profile(request):
    serializer = EditMembershipRequestSerializer(data=request.POST)
    if not serializer.is_valid():
        messages.error(request, 'First name, last name, and username must not be null')
        return redirect('midas:user_profile')

    req = serializer.save()

    request.user.first_name = req.first_name
    request.user.last_name = req.last_name
    request.user.username = req.username
    request.user.save()

    quota = get_object_or_404(Quota, pk=req.quota)
    assignment = Assignment.objects.create(user=request.user, quota=quota)
    if req.subteams:
        assignment.subteams.set(req.subteams)

    messages.success(request, 'Profile updated successfully!')
    return redirect('midas:user_profile')


class RenameTagSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100)  # NOT IntegerField
    new_tag_name = serializers.CharField(max_length=100)


def rename_tag(request):
    serializer = RenameTagSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    code = serializer.validated_data['code']
    new_tag_name = serializer.validated_data['new_tag_name']

    tag = get_object_or_404(ClaimedTag, owner=request.user, code=code)
    tag.name = new_tag_name
    tag.save()

    return redirect('midas:user_profile')


class DeleteTagSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100)


def delete_tag(request):
    serializer = DeleteTagSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    code = serializer.validated_data['code']

    tag = get_object_or_404(ClaimedTag, owner=request.user, code=code)

    tag.delete()
    messages.success(request, 'Tag deleted.')
    return redirect('midas:user_profile')


# def user_statistics(request):
#     call_command('update_statistics')

#     stats = Statistics.objects.filter(person=request.user).order_by('-date').first()

#     membership = (
#         Membership.objects.filter_effective()
#         .select_related('subteam')
#         .filter(person=request.user)
#         .first()
#     )

#     if membership:
#         quota_minutes_week = membership.job.quota * 60
#         subteam_name = membership.subteam.name
#     else:
#         quota_minutes_week = 9999 * 60
#         subteam_name = 'You are alone.'

#     # XXX: let's just assume that a month is exactly 4 weeks, noone's gonna notice, right? right?
#     # TODO: actually calculate amount of workdays in the month
#     quota_minutes_month = quota_minutes_week * 4

#     quota_week_met = stats.minutes_week >= quota_minutes_week
#     quota_month_met = stats.minutes_month >= quota_minutes_month

#     def format_time(minutes):
#         hours = minutes // 60
#         minutes = minutes % 60
#         s = f'{hours}h'
#         if minutes:
#             s += f' {minutes}m'
#         return s

#     return render(
#         request,
#         'midas/user_statistics.html',
#         {
#             # user info
#             'user_name': request.user.get_full_name(),
#             'user_role': subteam_name,
#             'user_status': user_status(request),
#             # totals
#             'total_hours_day': format_time(stats.minutes_day),
#             'total_hours_week': format_time(stats.minutes_week),
#             'total_hours_month': format_time(stats.minutes_month),
#             'total_hours_all': format_time(stats.total_minutes),
#             'average_hours_week': format_time(stats.average_week),
#             'quota_hours_week': format_time(quota_minutes_week),
#             # quotas
#             'quota_week_met': 'MET' if quota_week_met else 'UNMET',
#             'quota_month_met': 'MET' if quota_month_met else 'UNMET',
#             # js values (for echarts)
#             'script_data': {
#                 'total_hours_week': stats.minutes_week,
#                 'quota_hours_week': quota_minutes_week,
#             },
#         },
#     )


# class AddTagSerializer(serializers.Serializer):
#     tag_name = serializers.CharField()


# class ScanTagSerializer(serializers.Serializer):
#     tag = serializers.IntegerField()


# @api_view(['GET'])
# def export_user_logs(request):
#     qs = (
#         Log.objects.filter(tag__owner=request.user)
#         .select_related('tag', 'scanner')
#         .order_by('-time')
#     )
#     return logs_to_csv(qs)


# @api_view(['GET'])
# def check_registration(request, db_id):
#     tag = Tag.objects.filter(id=db_id, owner=request.user).first()
#     if tag is None:
#         return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)

#     state = tag.get_state()
#     state_str = state.value if state else None
#     return JsonResponse(
#         {
#             'status': 'success',
#             'claimed': state == TagState.CLAIMED,
#             'state': state_str,
#         }
#     )


# @api_view(['GET'])
# def user_tags(request):
#     tags = Tag.objects.filter(owner=request.user).all()

#     data = []
#     for tag in tags:
#         state = tag.get_state()
#         state_str = state.value if state else None
#         data.append(
#             {
#                 'tag_code': str(tag.tag) if tag.tag is not None else None,
#                 'tag_name': str(tag.name) if tag.name is not None else None,
#                 'tag_owner': tag.owner_name(),
#                 'tag_state': state_str,
#             }
#         )

#     return JsonResponse({'status': 'success', 'tags': data}, status=200)


# def fuel_guage(request):
#     try:
#         membership = Membership.objects.filter(person=request.user).first()
#         if not membership or not membership.job:
#             return JsonResponse(
#                 {
#                     'status': 'error',
#                     'message': 'No job assignment found for user.',
#                 },
#                 status=400,
#             )
#         member_quota = membership.job.quota
#         stats = Statistics.objects.filter(person=request.user).order_by('-date').first()
#         hours_week = stats.minutes_week / 60

#         percentage = (hours_week / member_quota) * 100

#         return JsonResponse(
#             {
#                 'status': 'Success',
#                 'data': {
#                     'quota': member_quota,
#                     'hours_week': hours_week,
#                     'amt_work_done': percentage,
#                 },
#             }
#         )
#     except Exception as e:
#         return JsonResponse(
#             {'status': 'error', 'message': f'Error retrieving data: {str(e)}'},
#             status=500,
#         )

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import serializers

from . import statistics
from .models import Assignment, ClaimedTag, PendingTag, Quota, Scanner, Session, Subteam

# from .utils import logs_to_csv


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
        Assignment.objects.filter(user=request.user)
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
        pending_tag, created = PendingTag.objects.get_or_create(
            owner=request.user,
            name=tag_name,
            defaults={'scanner': Scanner.objects.order_by('?').first()},
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
    today_date = timezone.now().date()
    all_stats = []

    # Loop through all users and get their statistics
    for user in User.objects.all():
        # Get current assignment
        assignment = (
            Assignment.objects.filter(user=user, starting_from__lte=today_date)
            .order_by('-starting_from')
            .first()
        )  # returns None if no assignment
        subteams = assignment.get_subteams() if assignment else 'No subteam'
        quota = assignment.quota.hours if assignment else 'No quota'
        user_stats = {
            'name': user.first_name + ' ' + user.last_name,
            'subteam': subteams,
            'quota': quota,
            'minutes_today': statistics.get_minutes_today(user, today_date),
            'minutes_this_week': statistics.get_minutes_this_week(user, today_date),
            'minutes_this_month': statistics.get_minutes_this_month(user, today_date),
            'total_minutes': statistics.get_total_minutes(user, today_date),
            'average_week': statistics.get_average_week(user, today_date),
        }
        all_stats.append(user_stats)

    return all_stats


class EditMembershipSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    subteams = serializers.ListField(child=serializers.IntegerField(), required=False)
    quota = serializers.IntegerField(required=False)


def edit_profile(request):
    serializer = EditMembershipSerializer(data=request.POST)
    if not serializer.is_valid():
        print(serializer.errors)
        messages.error(request, 'Please fill all fields correctly.')
        return redirect('midas:user_profile')

    data = serializer.validated_data
    user = request.user
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.username = data['username']
    user.save()

    assignment = (
        Assignment.objects.filter(user=user)
        .select_related('quota')
        .prefetch_related('subteams')
        .first()
    )
    if assignment:
        subteam_ids = request.POST.getlist('subteams')
        quota_id = request.POST.get('quota')

        if subteam_ids:
            assignment.subteams.set(subteam_ids)
        if quota_id:
            assignment.quota_id = quota_id
        assignment.save()

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


# @login_not_required
# def sign_up(request):
#     token = request.GET.get('token')

#     # Check if token exists in cache
#     if not token or not cache.get(f'register_token_{token}'):
#         return HttpResponseForbidden('Invalid or expired registration link.')

#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('midas:login')  # replace with your login URL
#     else:
#         form = RegistrationForm()

#     return render(request, 'midas/sign_up.html', {'form': form})


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

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from rest_framework import serializers

from .models import Assignment, ClaimedTag, PendingTag, Scanner, Session

# from .utils import logs_to_csv


# TODO: Refactor for Midas
class LogIn(LoginView):
    template_name = 'webui/login.html'
    next_page = reverse_lazy('index')

    def form_valid(self, form):
        user_name = form.get_user().get_full_name()
        messages.success(self.request, f'Welcome, comrade {user_name}')
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out')
    return redirect('login')


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
            reverse_lazy('user_profile') + f'?modal=tag_scan&tag={pending_tag.id}'
        )

    # Polling modal: check if tag was claimed
    if modal_name == 'tag_scan' and tag_param:
        # has this tag been moved to ClaimedTag by the scanner?
        pending_tag_exists = PendingTag.objects.filter(id=tag_param).exists()
        if not pending_tag_exists:
            # pending tag disappeared → must have been claimed
            return redirect(reverse_lazy('user_profile'))

    # Render profile page normally ---
    return render(
        request,
        'midas/user_profile.html',
        {
            'user_status': user_status(request),
            'assignment': assignment,
            'modal_name': modal_name,
            'claimed_tags': list(claimed_tags),
            'pending_tags': list(pending_tags),
        },
    )


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
#             return redirect('login')  # replace with your login URL
#     else:
#         form = RegistrationForm()

#     return render(request, 'webui/sign_up.html', {'form': form})


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
#         'webui/user_statistics.html',
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


# class EditMembershipSerializer(serializers.Serializer):
#     first_name = serializers.CharField()
#     last_name = serializers.CharField()
#     username = serializers.CharField()
#     job = serializers.IntegerField()
#     subteam = serializers.IntegerField()


# def edit_profile(request):
#     serializer = EditMembershipSerializer(data=request.POST)
#     if not serializer.is_valid():
#         messages.error(request, 'Please fill all fields')
#         return redirect('user_profile')

#     first_name = serializer.validated_data['first_name']
#     last_name = serializer.validated_data['last_name']
#     username = serializer.validated_data['username']
#     job_id = serializer.validated_data['job']
#     subteam_id = serializer.validated_data['subteam']

#     job = get_object_or_404(Job, pk=job_id)
#     subteam = get_object_or_404(SubTeam, pk=subteam_id)

#     current_membership = (
#         Membership.objects.filter_effective()
#         .filter(person=request.user)
#         .order_by('starting_from')
#         .last()
#     )

#     request.user.first_name = first_name
#     request.user.last_name = last_name
#     request.user.username = username
#     try:
#         request.user.save()
#     except IntegrityError:
#         messages.error(request, f'Username {username} is already taken!')
#         return redirect('user_profile')

#     if (
#         not current_membership
#         or not current_membership.job
#         or not current_membership.subteam
#         or current_membership.job.id != job.id
#         or current_membership.subteam.id != subteam.id
#     ):
#         Membership.objects.create(
#             person=request.user,
#             job=job,
#             subteam=subteam,
#         )

#     messages.success(request, 'Profile updated')
#     return redirect('user_profile')


# class DeleteTagSerializer(serializers.Serializer):
#     tag_id = serializers.IntegerField()


# def delete_tag(request):
#     serializer = DeleteTagSerializer(data=request.POST)
#     serializer.is_valid(raise_exception=True)

#     tag_id = serializer.validated_data['tag_id']

#     tag = get_object_or_404(Tag, pk=tag_id)

#     if tag.name == 'WebUI':
#         return JsonResponse(
#             {'status': 'error', 'message': 'Cannot delete WebUI tag'},
#             status=403,
#         )

#     tag.name = ''
#     tag.save()

#     return redirect('user_profile')


# class RenameTagSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     tag_name = serializers.CharField(max_length=100)


# def rename_tag(request):
#     serializer = RenameTagSerializer(data=request.POST)
#     serializer.is_valid(raise_exception=True)

#     tag_code = serializer.validated_data['id']
#     tag_name = serializer.validated_data['tag_name']

#     tag = get_object_or_404(Tag, pk=tag_code)

#     if tag.name == 'WebUI':
#         return JsonResponse(
#             {'status': 'error', 'message': 'Cannot edit WebUI tag'}, status=403
#         )
#     tag.name = tag_name
#     tag.save()
#     return redirect('user_profile')


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

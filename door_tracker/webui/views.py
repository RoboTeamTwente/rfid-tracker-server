from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.management import call_command
from django.db import IntegrityError
from django.db.models import Avg, Sum
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import (
    api_view,
)

# Import Custom Files
from .forms import RegistrationForm

# Create your views here.
from .models import (
    Job,
    Log,
    Membership,
    Scanner,
    Statistics,
    SubTeam,
    Tag,
    TagState,
    is_checked_in,
)
from .utils import logs_to_csv


def user_status(request):
    if is_checked_in(request.user):
        return 'CHECKED-IN'
    return 'CHECKED-OUT'


def index(request):
    logs = (
        Log.objects.filter(tag__owner=request.user)
        .select_related('tag')
        .order_by('-time')[:10]
    )

    return render(
        request,
        'webui/index.html',
        {
            'logs': logs,
            'user_status': user_status(request),
        },
    )


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


def serializer_error(serializer):
    msg = 'Invalid request:\n'
    for field, errors in serializer.errors.items():
        if field == 'non_field_errors':
            msg += '  general errors:\n'
        else:
            msg += f'  field {field}:\n'
        for error in errors:
            msg += f'    {error}\n'
    return msg


def minutes_today(request):
    today = timezone.localdate()  # gets the current date in the current timezone
    now = timezone.localtime()
    minutes_worked = 0

    logs = (
        Log.objects.filter(
            tag__owner=request.user,
            time__date=today,  # filter only logs that happened today
        )
        .select_related('tag')
        .order_by('time')
    )

    checkin_time = None
    first_log = True

    for log in logs:
        if log.type == Log.LogEntryType.CHECKIN:
            checkin_time = log.time
            first_log = False
        elif log.type == Log.LogEntryType.CHECKOUT:
            if checkin_time and not first_log:
                delta = timezone.localtime(log.time) - timezone.localtime(checkin_time)
                minutes_worked += int(delta.total_seconds() // 60)
                checkin_time = None
            elif first_log:
                # First log is a checkout with no prior checkin today
                midnight = timezone.make_aware(
                    timezone.datetime.combine(
                        timezone.localdate(log.time),
                        timezone.datetime.min.time(),
                    )
                )
                delta = timezone.localtime(log.time) - midnight
                minutes_worked += int(delta.total_seconds() // 60)
                first_log = False

    # If the last log was a checkin and no checkout yet, count time until now
    if checkin_time:
        delta = now - timezone.localtime(checkin_time)
        minutes_worked += int(delta.total_seconds() // 60)

    return minutes_worked


def minutes_week(request):
    today = timezone.localdate()
    start_of_week = today - timezone.timedelta(days=today.weekday())  # Monday

    total_week = (
        Statistics.objects.filter(
            person=request.user,
            date__date__gte=start_of_week,
            date__date__lte=today,
        ).aggregate(total=Sum('minutes_day'))['total']
        or 0
    )

    return total_week


def minutes_month(request):
    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    total_month = (
        Statistics.objects.filter(
            person=request.user,
            date__date__gte=start_of_month,
            date__date__lte=today,
        ).aggregate(total=Sum('minutes_day'))['total']
        or 0
    )

    return total_month


def save_statistics(request):
    # Get current time in the active timezone
    now = timezone.localtime()

    # Get today's date (without time) to filter existing statistics
    today_date = now.date()

    minutes_today_val = minutes_today(request)

    stats, created = Statistics.objects.update_or_create(
        person=request.user,
        date__date=today_date,  # filter by date portion only
        defaults={
            'minutes_day': minutes_today_val,
            'minutes_week': 0,
            'minutes_month': 0,
            'average_week': 0,
            'total_minutes': 0,
            'date': now,
        },
    )

    minutes_week_val = minutes_week(request)
    minutes_month_val = minutes_month(request)

    # Update only the week/month fields
    stats.minutes_week = minutes_week_val
    stats.minutes_month = minutes_month_val

    # Calculate avg and total
    agg = Statistics.objects.filter(person=request.user).aggregate(
        average_week=Avg('minutes_week'),
        total_minutes=Sum('minutes_day'),
    )

    average_week = agg['average_week'] or 0
    total_minutes = agg['total_minutes'] or 0

    if created:
        stats.save()  # full save on new record
    else:
        stats.save(
            update_fields=[
                'minutes_day',
                'minutes_week',
                'minutes_month',
                'average_week',
                'total_minutes',
            ]
        )

    return JsonResponse(
        {
            'minutes_day': minutes_today_val,
            'minutes_week': minutes_week_val,
            'minutes_month': minutes_month_val,
            'average_minutes': average_week,
            'total_minutes': total_minutes,
            'date': stats.date,
            'created': created,
        },
        status=200,
    )


class RegisterScanSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    card_id = serializers.CharField()


@csrf_exempt
@extend_schema(exclude=True)
@api_view(['POST'])
def register_scan(request):
    serializer = RegisterScanSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse(
            {'status': 'error', 'message': serializer_error(serializer)},
            status=400,
        )

    card_id = serializer.validated_data['card_id']
    scanner_id = serializer.validated_data['device_id']

    scanner = Scanner.objects.filter(pk=scanner_id).first()

    if not scanner:
        return JsonResponse(
            {'status': 'error', 'message': 'Scanner not authorized'}, status=403
        )

    tag = Tag.objects.select_related('owner').filter(tag=card_id).first()

    if tag is None:
        tag = Tag.objects.filter(tag=None).first()

    if tag is None:
        tag = Tag.objects.create(tag=card_id)

    match tag.get_state():
        case TagState.UNAUTHORIZED:
            Log.objects.create(
                type=Log.LogEntryType.UNKNOWN,
                scanner=scanner,
                tag=tag,
            )
            return JsonResponse(
                {'status': 'error', 'message': 'Card not registered'},
                status=404,
            )

        case TagState.PENDING_REGISTRATION:
            Log.objects.create(
                type=Log.LogEntryType.REGISTRATION,
                scanner=scanner,
                tag=tag,
            )
            tag.tag = card_id
            tag.save()
            call_command('update_statistics')
            hours_day = (
                Statistics.objects.filter(person=tag.owner).latest('date').minutes_day
                // 60
            )
            hours_week = (
                Statistics.objects.filter(person=tag.owner).latest('date').minutes_week
                // 60
            )
            return JsonResponse(
                {
                    'state': 'register',
                    'owner_name': tag.owner_name(),
                    'hours_day': hours_day,
                    'hours_week': hours_week,
                }
            )

        case TagState.CLAIMED:
            checkout = is_checked_in(tag.owner)
            Log.objects.create(
                type=(
                    Log.LogEntryType.CHECKOUT if checkout else Log.LogEntryType.CHECKIN
                ),
                scanner=scanner,
                tag=tag,
            )
            call_command('update_statistics')
            hours_day = (
                Statistics.objects.filter(person=tag.owner).latest('date').minutes_day
                // 60
            )
            hours_week = (
                Statistics.objects.filter(person=tag.owner).latest('date').minutes_week
                // 60
            )
            return JsonResponse(
                {
                    'state': 'checkout' if checkout else 'checkin',
                    'owner_name': tag.owner_name(),
                    'hours_day': hours_day,  # TODO
                    'hours_week': hours_week,  # TODO
                }
            )


class HealthcheckSerializer(serializers.Serializer):
    scanner_id = serializers.CharField()


@extend_schema(exclude=True)
@api_view(['POST'])
def healthcheck(request):
    serializer = HealthcheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    scanner_id = serializer.validated_data['scanner_id']

    try:
        Scanner.objects.get(pk=scanner_id)
        return JsonResponse(
            {'status': 'ok', 'message': 'Success'},
            status=200,
        )
    except Scanner.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Scanner not registered'},
            status=403,
        )


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
            return redirect('login')  # replace with your login URL
    else:
        form = RegistrationForm()

    return render(request, 'webui/sign_up.html', {'form': form})


def user_statistics(request):
    call_command('update_statistics')

    stats = Statistics.objects.filter(person=request.user).order_by('-date').first()

    membership = (
        Membership.objects.filter_effective()
        .select_related('subteam')
        .filter(person=request.user)
        .first()
    )

    if membership:
        quota_minutes_week = membership.job.quota * 60
        subteam_name = membership.subteam.name
    else:
        quota_minutes_week = 9999 * 60
        subteam_name = 'You are alone.'

    # XXX: let's just assume that a month is exactly 4 weeks, noone's gonna notice, right? right?
    # TODO: actually calculate amount of workdays in the month
    quota_minutes_month = quota_minutes_week * 4

    quota_week_met = stats.minutes_week >= quota_minutes_week
    quota_month_met = stats.minutes_month >= quota_minutes_month

    def format_time(minutes):
        hours = minutes // 60
        minutes = minutes % 60
        s = f'{hours}h'
        if minutes:
            s += f' {minutes}m'
        return s

    return render(
        request,
        'webui/user_statistics.html',
        {
            # user info
            'user_name': request.user.get_full_name(),
            'user_role': subteam_name,
            'user_status': user_status(request),
            # totals
            'total_hours_day': format_time(stats.minutes_day),
            'total_hours_week': format_time(stats.minutes_week),
            'total_hours_month': format_time(stats.minutes_month),
            'total_hours_all': format_time(stats.total_minutes),
            'average_hours_week': format_time(stats.average_week),
            'quota_hours_week': format_time(quota_minutes_week),
            # quotas
            'quota_week_met': 'MET' if quota_week_met else 'UNMET',
            'quota_month_met': 'MET' if quota_month_met else 'UNMET',
            # js values (for echarts)
            'script_data': {
                'total_hours_week': stats.minutes_week,
                'quota_hours_week': quota_minutes_week,
            },
        },
    )


class AddTagSerializer(serializers.Serializer):
    tag_name = serializers.CharField()


class ScanTagSerializer(serializers.Serializer):
    tag = serializers.IntegerField()


def user_profile(request):
    if request.POST.get('action') == 'add_tag':
        serializer = AddTagSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)

        tag_name = serializer.validated_data['tag_name']

        tag = Tag(name=tag_name, owner=request.user)
        tag.save()

        return redirect(
            reverse_lazy('user_profile', query={'modal': 'tag_scan', 'tag': tag.id})
        )

    if request.GET.get('modal') == 'tag_scan':
        serializer = ScanTagSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        tag_code = serializer.validated_data['tag']

        tag = get_object_or_404(Tag, pk=tag_code)

        if tag.get_state() == TagState.CLAIMED:
            return redirect('user_profile')

    tags = Tag.objects.get_authorized().filter(owner=request.user)
    membership = (
        Membership.objects.filter(person=request.user)
        .select_related('job', 'subteam')
        .order_by('-starting_from')
        .first()
    )

    return render(
        request,
        'webui/user_profile.html',
        {
            'jobs': Job.objects.all(),
            'membership': membership,
            'modal_name': request.GET.get('modal'),
            'request': request,
            'subteams': SubTeam.objects.all(),
            'tags': tags,
            'user': request.user,
            'user_status': user_status(request),
        },
    )


class EditMembershipSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    job = serializers.IntegerField()
    subteam = serializers.IntegerField()


def edit_profile(request):
    serializer = EditMembershipSerializer(data=request.POST)
    if not serializer.is_valid():
        messages.error(request, 'Please fill all fields')
        return redirect('user_profile')

    first_name = serializer.validated_data['first_name']
    last_name = serializer.validated_data['last_name']
    username = serializer.validated_data['username']
    job_id = serializer.validated_data['job']
    subteam_id = serializer.validated_data['subteam']

    job = get_object_or_404(Job, pk=job_id)
    subteam = get_object_or_404(SubTeam, pk=subteam_id)

    current_membership = (
        Membership.objects.filter_effective()
        .filter(person=request.user)
        .order_by('starting_from')
        .last()
    )

    request.user.first_name = first_name
    request.user.last_name = last_name
    request.user.username = username
    try:
        request.user.save()
    except IntegrityError:
        messages.error(request, f'Username {username} is already taken!')
        return redirect('user_profile')

    if (
        not current_membership
        or not current_membership.job
        or not current_membership.subteam
        or current_membership.job.id != job.id
        or current_membership.subteam.id != subteam.id
    ):
        Membership.objects.create(
            person=request.user,
            job=job,
            subteam=subteam,
        )

    messages.success(request, 'Profile updated')
    return redirect('user_profile')


class DeleteTagSerializer(serializers.Serializer):
    tag_id = serializers.IntegerField()


def delete_tag(request):
    serializer = DeleteTagSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    tag_id = serializer.validated_data['tag_id']

    tag = get_object_or_404(Tag, pk=tag_id)

    if tag.name == 'WebUI':
        return JsonResponse(
            {'status': 'error', 'message': 'Cannot delete WebUI tag'},
            status=403,
        )

    tag.name = ''
    tag.save()

    return redirect('user_profile')


class RenameTagSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tag_name = serializers.CharField(max_length=100)


def rename_tag(request):
    serializer = RenameTagSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    tag_code = serializer.validated_data['id']
    tag_name = serializer.validated_data['tag_name']

    tag = get_object_or_404(Tag, pk=tag_code)

    if tag.name == 'WebUI':
        return JsonResponse(
            {'status': 'error', 'message': 'Cannot edit WebUI tag'}, status=403
        )
    tag.name = tag_name
    tag.save()
    return redirect('user_profile')


@extend_schema(exclude=True)
@api_view(['GET'])
def export_user_logs(request):
    qs = (
        Log.objects.filter(tag__owner=request.user)
        .select_related('tag', 'scanner')
        .order_by('-time')
    )
    return logs_to_csv(qs)


@extend_schema(exclude=True)
@api_view(['GET'])
def check_registration(request, db_id):
    tag = Tag.objects.filter(id=db_id, owner=request.user).first()
    if tag is None:
        return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)

    state = tag.get_state()
    state_str = state.value if state else None
    return JsonResponse(
        {
            'status': 'success',
            'claimed': state == TagState.CLAIMED,
            'state': state_str,
        }
    )


@extend_schema(exclude=True)
@api_view(['GET'])
def user_tags(request):
    tags = Tag.objects.filter(owner=request.user).all()

    data = []
    for tag in tags:
        state = tag.get_state()
        state_str = state.value if state else None
        data.append(
            {
                'tag_code': str(tag.tag) if tag.tag is not None else None,
                'tag_name': str(tag.name) if tag.name is not None else None,
                'tag_owner': tag.owner_name(),
                'tag_state': state_str,
            }
        )

    return JsonResponse({'status': 'success', 'tags': data}, status=200)


def fuel_guage(request):
    try:
        membership = Membership.objects.filter(person=request.user).first()
        if not membership or not membership.job:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'No job assignment found for user.',
                },
                status=400,
            )
        member_quota = membership.job.quota
        stats = Statistics.objects.filter(person=request.user).order_by('-date').first()
        hours_week = stats.minutes_week / 60

        percentage = (hours_week / member_quota) * 100

        return JsonResponse(
            {
                'status': 'Success',
                'data': {
                    'quota': member_quota,
                    'hours_week': hours_week,
                    'amt_work_done': percentage,
                },
            }
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': f'Error retrieving data: {str(e)}'},
            status=500,
        )


class AutoCheckoutSerializer(serializers.Serializer):
    checkout_time = serializers.DateTimeField(required=True)


@extend_schema(exclude=True)
@api_view(['POST'])
def auto_checkout(request):
    serializer = AutoCheckoutSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse(
            {'status': 'error', 'message': serializer_error(serializer)},
            status=400,
        )

    checkout_time = serializer.validated_data['checkout_time']
    current_time = timezone.now()

    if checkout_time > current_time:
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Checkout time cannot be in the future.',
            },
            status=400,
        )

    if not is_checked_in(request.user):
        return JsonResponse(
            {'status': 'error', 'message': 'User is not currently checked in.'},
            status=400,
        )

    tag = Tag.objects.filter(owner=request.user, name='WebUI').first()
    if not tag:
        return JsonResponse(
            {'status': 'error', 'message': 'No valid tag found for user.'},
            status=404,
        )

    log = Log.objects.create(
        type=Log.LogEntryType.CHECKOUT,
        tag=tag,
        time=checkout_time,
    )

    return JsonResponse(
        {
            'status': 'success',
            'state': log.type,
            'state_display': log.get_type_display(),
            'date': log.time.isoformat(),
            'tag': str(tag),
        },
        status=201,
    )

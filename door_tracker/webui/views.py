import csv
from base64 import b64decode, b64encode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.db.models import Avg, Sum
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework import serializers
from rest_framework.decorators import api_view

# Import Custom Files
from . import utils  # -> Helper functions
from .forms import RegistrationForm

# Create your views here.
from .models import (
    Log,
    Membership,
    Scanner,
    Statistics,
    Tag,
    TagState,
    is_checked_in,
)


def index(request):
    # Greetings from the Ancient One
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'webui/index.html', {'username': request.user.username})


@ensure_csrf_cookie
def new_login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse(
                    {
                        'status': 'success',
                        'message': f'Welcome Comrade {username}',
                    },
                    status=200,
                )
            else:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Invalid username or password',
                    },
                    status=401,
                )
        else:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid username or password'},
                status=400,
            )

    return render(request, 'webui/login.html')


def new_logout(request):
    logout(request)
    messages.success(request, 'Logged out')
    return redirect('login')


@utils.require_authentication
def check_status(request):
    last_log = (
        Log.objects.filter(tag__owner=request.user)
        .select_related('tag')
        .order_by('-time')
        .first()
    )

    if not last_log:
        # No logs yet for this user
        return JsonResponse(
            {
                'status': 'success',
                'state': None,
                'state_display': None,
                'date': None,
            },
            status=200,
        )

    return JsonResponse(
        {
            'status': 'success',
            'state': last_log.type,
            'state_display': last_log.get_type_display(),
            'date': last_log.time.isoformat(),
        },
        status=200,
    )


class Base64Field(serializers.Field):
    def to_representation(self, value):
        return b64encode(value)

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail('type_error', input_type=type(data).__name__)
        return b64decode(data)

    default_error_messages = {
        'type_error': 'Incorrect type. Expected a string, but got {input_type}'
    }


class ChangeStatusSerializer(serializers.Serializer):
    tag_id = Base64Field(required=True)


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


@api_view(['POST'])
@utils.require_authentication
def change_status(request):
    # at this point, request.user is guaranteed authenticated
    serializer = ChangeStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse(
            {'status': 'error', 'message': serializer_error(serializer)},
            status=400,
        )

    tag_scanned = (
        Tag.objects.select_related('owner')
        .filter(id=serializer.validated_data.tag_id, owner=request.user)
        .first()
    )
    if not tag_scanned:
        return JsonResponse(
            {'status': 'error', 'message': 'Tag not found or not yours.'},
            status=404,
        )

    last_log = Log.objects.filter(tag=tag_scanned).order_by('-time').first()
    new_type = (
        Log.LogEntryType.CHECKIN
        if not last_log or last_log.type == Log.LogEntryType.CHECKOUT
        else Log.LogEntryType.CHECKOUT
    )

    log = Log.objects.create(type=new_type, tag=tag_scanned)

    return JsonResponse(
        {
            'status': 'success',
            'state': log.type,
            'state_display': log.get_type_display(),
            'date': log.time.isoformat(),
            'tag': str(tag_scanned),
        },
        status=201,
    )


def current_user_data(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'status': 'error', 'message': 'Log in to view data.'},
            status=400,
        )

    logs = (
        Log.objects.filter(tag__owner=request.user)
        .select_related('tag')
        .order_by('-time')
    )

    data = [
        {
            'id': log.id,
            'type': log.get_type_display(),
            'time': log.time.isoformat(),
            'tag': str(log.tag),
            'user_id': log.tag.owner_id if (log.tag and log.tag.owner_id) else None,
        }
        for log in logs
    ]

    return JsonResponse({'status': 'success', 'logs': data}, status=200)


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

    stats.average_week = average_week
    stats.total_minutes = total_minutes

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


def get_statistics(request):
    save_statistics(request)
    myStats = Statistics.objects.filter(person=request.user).last()
    if not myStats:
        return JsonResponse(
            {'status': 'error', 'message': 'No statistics found'}, status=404
        )

    myMembership = Membership.objects.filter(person=request.user).first()
    if not myMembership or not myMembership.job:
        return JsonResponse(
            {'status': 'error', 'message': 'No membership/job found'},
            status=404,
        )

    weeklyQuota = myMembership.job.quota * 60
    monthlyQuota = weeklyQuota * 4
    print(weeklyQuota)

    flagWeeklyQuota = myStats.minutes_week >= weeklyQuota
    flagMonthlyQuota = myStats.minutes_month >= monthlyQuota

    data = {
        'status': 'success',
        'stats': {
            'date': myStats.date.isoformat(),
            'minutes_day': myStats.minutes_day,
            'minutes_week': myStats.minutes_week,
            'minutes_month': myStats.minutes_month,
            'average_week': myStats.average_week,
            'total_minutes': myStats.total_minutes,
            'quotaWeekly': flagWeeklyQuota,
            'quotaMonthly': flagMonthlyQuota,
            'user': request.user.username,
        },
    }
    return JsonResponse(data, status=200)


class RegisterScanSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    card_id = serializers.CharField()


@csrf_exempt
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
        tag = Tag(tag=card_id)
        tag.save()

    log = Log(scanner=scanner, tag=tag)

    match tag.get_state():
        case TagState.UNAUTHORIZED:
            log.type = Log.LogEntryType.UNKNOWN
            log.save()
            return JsonResponse(
                {'status': 'error', 'message': 'Card not registered'},
                status=404,
            )

        case TagState.PENDING_REGISTRATION:
            log.type = Log.LogEntryType.REGISTRATION
            log.save()
            tag.tag = card_id
            tag.save()
            return JsonResponse(
                {
                    'state': 'register',
                    'name': tag.owner_name(),
                    'dailyhours': 42,
                    'weeklyhours': 420,
                }
            )

        case TagState.CLAIMED:
            checkout = is_checked_in(tag.owner)
            log.type = (
                Log.LogEntryType.CHECKOUT if checkout else Log.LogEntryType.CHECKIN
            )
            log.save()
            return JsonResponse(
                {
                    'state': 'checkout' if checkout else 'checkin',
                    'name': tag.owner_name(),
                    'dailyhours': 42,  # TODO
                    'weeklyhours': 420,  # TODO
                }
            )


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
    return render(request, 'webui/user_statistics.html')


def user_profile(request):
    return render(request, 'webui/user_profile.html')


class ExportSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())


@api_view(['GET'])
def export(request):
    serializer = ExportSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    ids = serializer.validated_data['ids']
    qs = Log.objects.filter(pk__in=ids)
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response, dialect='excel')
    writer.writerow(['time', 'type', 'tag', 'owner_first', 'owner_last', 'scanner'])
    writer.writerows(
        qs.values_list(
            'time',
            'type',
            'tag__name',
            'tag__owner__first_name',
            'tag__owner__last_name',
            'scanner__name',
        )
    )
    return response


@api_view(['POST'])
def create_pending_reg(request):
    tag_name = request.data.get('name', 'pending')  # fallback if not provided

    tag = Tag(name=tag_name, owner=request.user)
    tag.save()

    state = tag.get_state()
    state_str = state.value if state else None

    return JsonResponse(
        {
            'status': 'success',
            'tag_data': {
                'DB ID': tag.id,
                'tag ID': tag.tag,
                'tag Name': tag.name,
                'tag Owner': tag.owner_name(),
                'tag State': state_str,
            },
        }
    )


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


@api_view(['GET'])
def user_tags(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    tags = Tag.objects.filter(owner=request.user).all()

    data = []
    for tag in tags:
        state = tag.get_state()
        state_str = state.value if state else None
        data.append(
            {
                'tag ID': str(tag.tag) if tag.tag is not None else None,
                'tag Name': str(tag.name) if tag.name is not None else None,
                'tag Owner': tag.owner_name(),
                'tag State': state_str,
            }
        )

    return JsonResponse({'status': 'success', 'tags': data}, status=200)


# @api_view(["GET"])
# def get_user_status(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

#     user_status =

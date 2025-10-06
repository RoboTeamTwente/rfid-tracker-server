from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import (
    CharField,
    DateTimeField,
    IntegerField,
    Serializer,
)

from .models import (
    Checkin,
    Checkout,
    ClaimedTag,
    LogType,
    PendingTag,
    Scanner,
    Session,
)
from .statistics import get_minutes_this_week, get_minutes_today


def serializer_error(serializer):
    msg = 'Invalid request:\n'
    for field, errors in serializer.errors.items():
        if field == 'non_field_errors':
            msg += '  general errors:\n'
        else:
            msg += f'  field {field}:\n'
        for error in errors:
            msg += f'    {error}\n'
    return Response(
        {'status': 'error', 'message': msg},
        status=400,
    )


@api_view(['GET'])
def api_root(request, format=None):
    return Response(
        {
            'register_scan': reverse('register_scan', request=request, format=format),
        }
    )


@dataclass
class RegisterScanRequest:
    device_id: str
    tag_id: str


@dataclass
class RegisterScanResponse:
    state: str
    owner_name: str
    hours_day: int
    hours_week: int

    @classmethod
    def make(self, state, user, date):
        return RegisterScanResponse(
            state=state,
            owner_name=user.get_full_name(),
            hours_day=get_minutes_today(user, date) // 60,
            hours_week=get_minutes_this_week(user, date) // 60,
        )


class RegisterScanRequestSerializer(Serializer):
    device_id = CharField()
    tag_id = CharField()

    def create(self, validated_data):
        return RegisterScanRequest(**validated_data)


class RegisterScanResponseSerializer(Serializer):
    state = CharField()
    owner_name = CharField()
    hours_day = IntegerField()
    hours_week = IntegerField()

    def create(self, validated_data):
        return RegisterScanResponse(**validated_data)


@api_view(['POST'])
def register_scan(request):
    serializer = RegisterScanRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return serializer_error(serializer)

    args = serializer.save()

    scanner = Scanner.objects.filter(pk=args.device_id).first()
    if not scanner:
        return Response(
            {'status': 'error', 'message': 'Scanner not authorized'},
            status=403,
        )

    # try to register a pending tag

    try:
        with transaction.atomic():
            claimed_tag = ClaimedTag.objects.create(
                owner=scanner.pending_tag.owner,
                name=scanner.pending_tag.name,
                code=args.tag_id,
            )
            scanner.pending_tag.delete()
    except PendingTag.DoesNotExist:
        pass
    else:
        user = claimed_tag.owner
        today = timezone.now().date()
        res = RegisterScanResponse.make('register', user, today)
        serializer = RegisterScanResponseSerializer(res)
        return Response(serializer.data)

    # try to check out

    try:
        with transaction.atomic():
            claimed_tag = ClaimedTag.objects.select_related('owner').get(
                code=args.tag_id
            )
            current_session = Session.objects.get(
                user=claimed_tag.owner,
                checkin__time__date=timezone.now().date(),
                checkout__isnull=True,
            )
            Checkout.objects.create(
                type=LogType.TAG,
                tag=claimed_tag,
                session=current_session,
            )
    except (ClaimedTag.DoesNotExist, Session.DoesNotExist):
        pass
    else:
        user = claimed_tag.owner
        today = timezone.now().date()
        res = RegisterScanResponse.make('checkout', user, today)

        serializer = RegisterScanResponseSerializer(res)
        return Response(serializer.data)

    # try to check in

    try:
        with transaction.atomic():
            claimed_tag = ClaimedTag.objects.select_related('owner').get(
                code=args.tag_id
            )
            new_session = Session.objects.create(user=claimed_tag.owner)
            Checkin.objects.create(
                type=LogType.TAG,
                tag=claimed_tag,
                session=new_session,
            )
    except ClaimedTag.DoesNotExist:
        pass
    else:
        user = claimed_tag.owner
        today = timezone.now().date()
        res = RegisterScanResponse.make('checkin', user, today)
        serializer = RegisterScanResponseSerializer(res)
        return Response(serializer.data)

    return Response(
        {'status': 'error', 'message': 'Card not registered'},
        status=404,
    )


class HealthcheckRequestSerializer(Serializer):
    scanner_id = CharField()

    def create(self, validated_data):
        return validated_data['scanner_id']


@api_view(['POST'])
def healthcheck(request):
    serializer = HealthcheckRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return serializer_error(serializer)

    if not Scanner.objects.filter(pk=serializer.save()).exists():
        return Response(
            {'status': 'error', 'message': 'Scanner not registered'},
            status=403,
        )

    return Response({'status': 'ok'})


class CheckoutSerializer(Serializer):
    time = DateTimeField()

    def create(self, validated_data):
        return validated_data['time']


@api_view(['POST'])
def checkout(request):
    serializer = CheckoutSerializer(data=request.data)
    if not serializer.is_valid():
        return serializer_error(serializer)
    checkout_time = serializer.save()

    if checkout_time > timezone.now():
        return Response(
            {
                'status': 'error',
                'message': 'Cannot checkout in the future',
            },
            status=400,
        )

    try:
        with transaction.atomic():
            session = Session.objects.get(
                user=request.user,
                checkin__time__date=checkout_time.date(),
                checkout__isnull=True,
            )
            checkout = Checkout.objects.create(
                type=LogType.REMOTE,
                time=checkout_time,
                session=session,
            )
    except Session.DoesNotExist:
        return Response(
            {
                'status': 'error',
                'message': 'There are no matching sessions',
            },
            status=404,
        )
    else:
        return Response(
            {
                'status': 'ok',
                'date': checkout.time.isoformat(),
            },
            status=201,
        )

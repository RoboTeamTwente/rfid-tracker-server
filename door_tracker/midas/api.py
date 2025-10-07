from dataclasses import dataclass

from django.db import transaction
from django.db.models import TextChoices
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    extend_schema_serializer,
)
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import (
    CharField,
    ChoiceField,
    DateTimeField,
    HiddenField,
    IntegerField,
    Serializer,
)
from rest_framework.settings import api_settings

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


@dataclass
class APIResponse:
    status: str
    message: str

    @classmethod
    def success(cls, message=None):
        return APIResponse(status='ok', message=message)

    @classmethod
    def error(cls, message=None):
        return APIResponse(status='error', message=message)


class APIResponseSerializer(Serializer):
    status = CharField()
    message = CharField(required=False)

    def create(self, validated_data):
        return APIResponse(**validated_data)


@dataclass
class RegisterScanRequest:
    device_id: str
    tag_id: str


class RegisterScanState(TextChoices):
    REGISTER = 'register', 'Tag registered'
    CHECKIN = 'checkin', 'User checked in'
    CHECKOUT = 'checkout', 'User checked out'


@dataclass
class RegisterScanResponse:
    state: RegisterScanState
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


@extend_schema_serializer(
    deprecate_fields=['card_id'],
    examples=[
        OpenApiExample(
            'example',
            value={
                'device_id': '44bb652ea2a696e1b2a7ce412f24a46d',
                'tag_id': 'DEADBEEF',
            },
        ),
    ],
)
class RegisterScanRequestSerializer(Serializer):
    device_id = CharField(label='Scanner ID')
    tag_id = CharField(required=False, label='Tag ID')
    card_id = CharField(required=False, source='tag_id', label='Tag ID')

    def validate(self, attrs):
        if 'tag_id' not in attrs and 'card_id' not in attrs:
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: 'Required field missing: one of tag_id, card_id'
                }
            )
        return super().validate(attrs)

    def create(self, validated_data):
        return RegisterScanRequest(**validated_data)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Registration',
            value={
                'state': 'register',
                'owner_name': 'John Doe',
                'hours_day': 42,
                'hours_week': 420,
            },
        ),
        OpenApiExample(
            'Check-in',
            value={
                'state': 'checkin',
                'owner_name': 'John Doe',
                'hours_day': 42,
                'hours_week': 420,
            },
        ),
        OpenApiExample(
            'Check-out',
            value={
                'state': 'checkout',
                'owner_name': 'John Doe',
                'hours_day': 42,
                'hours_week': 420,
            },
        ),
    ],
)
class RegisterScanResponseSerializer(Serializer):
    state = ChoiceField(choices=RegisterScanState.choices)
    owner_name = CharField()
    hours_day = IntegerField()
    hours_week = IntegerField()

    def create(self, validated_data):
        return RegisterScanResponse(**validated_data)


@extend_schema(
    operation_id='register_scan',
    auth=[],
    request=RegisterScanRequestSerializer,
    responses={
        200: RegisterScanResponseSerializer,
        403: APIResponseSerializer,
        404: APIResponseSerializer,
    },
)
@api_view(['POST'])
def register_scan(request):
    """Register tag scan

    This endpoint is called by the scanner every time it scans a tag.
    """

    serializer = RegisterScanRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return serializer_error(serializer)

    args = serializer.save()

    scanner = Scanner.objects.filter(pk=args.device_id).first()
    if not scanner:
        res = APIResponse.error('Scanner not authorized')
        s = APIResponseSerializer(res)
        return Response(s.data, status=403)

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
        res = RegisterScanResponse.make(RegisterScanState.REGISTER, user, today)
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
                checkin__time__date=timezone.now(),
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
        res = RegisterScanResponse.make(RegisterScanState.CHECKOUT, user, today)

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
        res = RegisterScanResponse.make(RegisterScanState.CHECKIN, user, today)
        serializer = RegisterScanResponseSerializer(res)
        return Response(serializer.data)

    # nothing worked, return a generic error

    res = APIResponse.error('Card not registered')
    s = APIResponseSerializer(res)
    return Response(s.data, status=404)


class HealthcheckRequestSerializer(Serializer):
    scanner_id = CharField()

    def create(self, validated_data):
        return validated_data['scanner_id']


@extend_schema(
    operation_id='healthcheck',
    auth=[],
    request=HealthcheckRequestSerializer,
    responses={
        200: APIResponseSerializer,
        403: APIResponseSerializer,
    },
)
@api_view(['POST'])
def healthcheck(request):
    """Mark the scanner as alive

    This endpoint is called by the scanner every 30 seconds. If the
    scanner does not do it in 5 minutes, it is declared dead.

    TODO: actually check this
    """
    serializer = HealthcheckRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return serializer_error(serializer)

    if not Scanner.objects.filter(pk=serializer.save()).exists():
        res = APIResponse.error('Scanner not registered')
        s = APIResponseSerializer(res)
        return Response(s.data, status=403)

    res = APIResponse.success()
    s = APIResponseSerializer(res)
    return Response(s.data)


@dataclass
class CheckoutResponse:
    time: timezone.datetime


class CheckoutRequestSerializer(Serializer):
    time = DateTimeField()

    def create(self, validated_data):
        return validated_data['time']


class CheckoutResponseSerializer(Serializer):
    status = HiddenField(default='ok')
    date = DateTimeField()

    def create(self, validated_data):
        return CheckoutResponse(**validated_data)


@extend_schema(
    operation_id='checkout',
    request=CheckoutRequestSerializer,
    responses={
        201: CheckoutResponseSerializer,
        400: APIResponseSerializer,
        404: APIResponseSerializer,
    },
)
@api_view(['POST'])
def checkout(request):
    """Check out remotely

    This endpoint is called from frontend to check a user out remotely.
    """
    serializer = CheckoutRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return serializer_error(serializer)
    checkout_time = serializer.save()

    if checkout_time > timezone.now():
        res = APIResponse.error('Cannot checkout in the future')
        s = APIResponseSerializer(res)
        return Response(s.data, status=400)

    try:
        with transaction.atomic():
            session = Session.objects.get(
                user=request.user,
                checkin__time__date=checkout_time,
                checkout__isnull=True,
            )
            checkout = Checkout.objects.create(
                type=LogType.REMOTE,
                time=checkout_time,
                session=session,
            )
    except Session.DoesNotExist:
        res = APIResponse.error('There are no matching sessions')
        s = APIResponseSerializer(res)
        return Response(s.data, status=404)
    else:
        res = CheckoutResponse(time=checkout.time)
        s = CheckoutResponseSerializer(res)
        return Response(s.data, status=201)

from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.db.models import OuterRef, Subquery
from django.db.models.aggregates import Max
from django.utils import timezone


class Log(models.Model):
    class LogEntryType(models.TextChoices):
        CHECKIN = 'IN', 'Check-in'
        CHECKOUT = 'OUT', 'Check-out'
        UNKNOWN = 'WTF', 'Card not linked'
        REGISTRATION = 'REG', 'Card registered'

    type = models.CharField(max_length=3, choices=LogEntryType.choices)
    scanner = models.ForeignKey(
        'Scanner',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    tag = models.ForeignKey(
        'Tag',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    time = models.DateTimeField(default=timezone.now)

    def person(self):
        if not self.tag:
            return 'WebUI'
        return str(self.tag)

    def __str__(self):
        return ' | '.join([str(self.time), self.type, self.person() or '-'])


class Membership(models.Model):
    person = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='memberships'
    )
    subteam = models.ForeignKey(
        'SubTeam',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='members',
    )
    job = models.ForeignKey('Job', blank=True, null=True, on_delete=models.CASCADE)
    starting_from = models.DateTimeField(default=timezone.now)

    class MembershipManager(models.Manager):
        def filter_effective(self):
            qs = self.all()
            return qs.filter(
                starting_from=Subquery(
                    qs.filter(person=OuterRef('person'))
                    .values('person')
                    .annotate(starting_from=Max('starting_from'))
                    .values('starting_from')
                ),
            )

    objects = MembershipManager()


class TagState(Enum):
    CLAIMED = 'claimed'
    PENDING_REGISTRATION = 'pending_registration'
    UNAUTHORIZED = 'unauthorized'


class Tag(models.Model):
    tag = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True)
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='tags',
    )

    def owner_name(self):
        if not self.owner:
            return None
        return self.owner.get_full_name()

    def tag_id(self):
        return self.tag

    def status(self):
        match self.get_state():
            case TagState.CLAIMED:
                return 'claimed'
            case TagState.PENDING_REGISTRATION:
                return 'pending registration'
            case TagState.UNAUTHORIZED:
                return 'unauthorized'

    def get_state(self):
        has_tag = self.tag is not None
        has_name = self.name != ''
        has_owner = self.owner is not None

        # T N O State
        # T T T CLAIMED
        # F T T PENDING_REGISTRATION
        # * * * UNAUTHORIZED

        if has_name and has_owner:
            if has_tag:
                return TagState.CLAIMED
            else:
                return TagState.PENDING_REGISTRATION
        else:
            return TagState.UNAUTHORIZED

    def __str__(self):
        n = self.name
        if not n:
            n = 'deleted tag'
        if self.owner:
            n += f' ({self.owner_name()})'
        return n

    class TagManager(models.Manager):
        def get_authorized(self):
            return self.filter(owner__isnull=False).exclude(name='')

        def get_pending(self):
            return self.get_authorized().filter(tag__isnull=True).first()

    objects = TagManager()


class SubTeam(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subteam'


class Job(models.Model):
    name = models.CharField()
    quota = models.IntegerField(verbose_name='Quota (hours per week)')

    def __str__(self):
        return f'{self.name} ({self.quota} hrs/week)'


class Statistics(models.Model):
    person = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='statistics'
    )
    date = models.DateTimeField()
    minutes_day = models.IntegerField()
    minutes_week = models.IntegerField()
    minutes_month = models.IntegerField()
    average_week = models.IntegerField()
    total_minutes = models.IntegerField()


class Scanner(models.Model):
    id = models.CharField(primary_key=True)
    name = models.CharField()

    def __str__(self):
        return self.name


def is_checked_in(user):
    last_log = (
        Log.objects.filter(tag__owner=user)
        .exclude(type=Log.LogEntryType.REGISTRATION)
        .order_by('-time')
        .first()
    )
    return last_log is not None and last_log.type == Log.LogEntryType.CHECKIN

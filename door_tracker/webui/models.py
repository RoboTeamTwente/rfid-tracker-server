from django.contrib.auth.models import User
from django.db import models
from django.db.models.aggregates import Max
from django.db.models import OuterRef, Subquery
from django.utils import timezone


class Log(models.Model):
    class LogEntryType(models.TextChoices):
        CHECKIN = 'IN', 'Check-in'
        CHECKOUT = 'OUT', 'Check-out'
        UNKNOWN = 'WTF', 'Card not linked'

    type = models.CharField(max_length=3, choices=LogEntryType.choices)
    tag = models.ForeignKey(
        'Tag', blank=True, null=True, on_delete=models.CASCADE, related_name='logs'
    )
    time = models.DateTimeField(auto_now_add=True)

    def person(self):
        if not self.tag:
            return 'WebUI'
        if self.tag.is_claimed():
            return f'{self.tag.owner.get_full_name()} ({self.tag.name})'
        return '-'

    def __str__(self):
        return ' — '.join([str(self.time), self.type, self.person()])


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


class Tag(models.Model):
    tag = models.BinaryField()
    name = models.CharField(blank=True)
    owner = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE, related_name='tags'
    )

    def owner_name(self):
        return self.owner.get_full_name()

    def is_claimed(self):
        return self.owner is not None

    def binary_id(self):
        return self.tag.hex().upper()

    def __str__(self):
        n = self.name
        if not n:
            n = 'unnamed'
        if self.owner:
            n += f' ({self.owner_name()})'
        return n


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

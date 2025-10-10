import secrets

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import OuterRef, Subquery
from django.db.models.aggregates import Max
from django.utils import timezone


class LogType(models.TextChoices):
    TAG = 'tag', 'tag scan'
    REMOTE = 'remote', 'remote'


class Log(models.Model):
    type = models.CharField(choices=LogType)
    time = models.DateTimeField(default=timezone.now)

    def clean(self):
        if self.type != LogType.TAG and self.tag is not None:
            raise ValidationError(
                {
                    'tag': f'Tag must not be set when type field is not "{LogType.TAG.label}"',
                }
            )

        if self.session and self.tag and self.session.user.id != self.tag.owner.id:
            raise ValidationError(
                {
                    'tag': f'This tag does not belong to {self.session.user.get_full_name()}'
                }
            )

    class Meta:
        abstract = True


class Checkin(Log):
    tag = models.ForeignKey(
        'ClaimedTag',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='checkins',
    )
    session = models.OneToOneField(
        'Session',
        on_delete=models.CASCADE,
        related_name='checkin',
    )


class Checkout(Log):
    tag = models.ForeignKey(
        'ClaimedTag',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='checkouts',
    )
    session = models.OneToOneField(
        'Session',
        on_delete=models.CASCADE,
        related_name='checkout',
    )


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')


class ClaimedTag(models.Model):
    code = models.CharField(primary_key=True)
    name = models.CharField()
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='claimed_tags'
    )

    def __str__(self):
        return f'{self.name} ({self.owner.get_full_name()})'


def _generate_scanner_id():
    """Generate an ID for a new scanner."""
    return secrets.token_hex(16)


class Scanner(models.Model):
    id = models.CharField(primary_key=True, default=_generate_scanner_id)
    name = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.name or '-'


class PendingTag(models.Model):
    name = models.CharField(null=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pending_tags'
    )
    scanner = models.OneToOneField(
        'Scanner', on_delete=models.RESTRICT, related_name='pending_tag'
    )


class Quota(models.Model):
    name = models.CharField()
    hours = models.IntegerField()

    def __str__(self):
        return f'{self.name} ({self.hours} hrs/week)'


class Assignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    quota = models.ForeignKey('Quota', on_delete=models.RESTRICT)
    subteams = models.ManyToManyField('Subteam')
    starting_from = models.DateTimeField(default=timezone.now)

    def subteam_names(self):
        return ', '.join([subteam.name for subteam in self.subteams.all()])

    class AssignmentManager(models.Manager):
        def filter_current(self):
            qs = self.all()
            return qs.filter(
                starting_from=Subquery(
                    qs.filter(
                        user=OuterRef('user'),
                        starting_from__lte=timezone.now(),
                    )
                    .values('user')
                    .annotate(starting_from=Max('starting_from'))
                    .values('starting_from')
                ),
            )

    objects = AssignmentManager()


class Subteam(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

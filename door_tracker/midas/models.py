import secrets

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Log(models.Model):
    type = models.CharField()
    time = models.DateTimeField(default=timezone.now)
    tag = models.ForeignKey(
        'ClaimedTag', on_delete=models.SET_NULL, null=True, blank=True
    )


class Session(models.Model):
    checkin = models.OneToOneField(
        'Log', on_delete=models.CASCADE, related_name='checkin_session'
    )
    checkout = models.OneToOneField(
        'Log',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='checkout_session',
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class ClaimedTag(models.Model):
    code = models.CharField(primary_key=True)
    name = models.CharField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class TagManager(models.Manager):
        def get_authorized(self):
            return self.filter(owner__isnull=False).exclude(name='')


class Scanner(models.Model):
    def generate_scanner_id():
        """Generate an ID for a new scanner."""
        return secrets.token_hex(16)

    id = models.CharField(primary_key=True, default=generate_scanner_id)
    name = models.CharField(null=True, blank=True)


class PendingTag(models.Model):
    name = models.CharField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    scanner = models.OneToOneField('Scanner', on_delete=models.CASCADE)


class Quota(models.Model):
    name = models.CharField(null=True, blank=True)
    hours = models.IntegerField()


class Assignment(models.Model):
    starting_from = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quota = models.ForeignKey('Quota', on_delete=models.CASCADE)


class Subteam(models.Model):
    name = models.CharField()


class SubteamMembership(models.Model):
    period = models.ForeignKey('Assignment', on_delete=models.CASCADE)
    subteam_id = models.ForeignKey('Subteam', on_delete=models.CASCADE)

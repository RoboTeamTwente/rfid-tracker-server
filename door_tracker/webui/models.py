from django.db import models
from django.utils import timezone


class Log(models.Model):
    class LogEntryType(models.TextChoices):
        CHECKIN = 'IN', 'Check-in'
        CHECKOUT = 'OUT', 'Check-out'
        UNKNOWN = 'WTF', 'Card not linked'

    type = models.CharField(max_length=3, choices=LogEntryType.choices)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='logs')
    time = models.DateTimeField(auto_now_add=True)

    def person(self):
        if self.tag.is_claimed():
            return f'{self.tag.owner.name} ({self.tag.name})'
        else:
            return '-'

    def __str__(self):
        return ' — '.join([str(self.time), self.type, self.person()])


class Membership(models.Model):
    person = models.ForeignKey(
        'Person', on_delete=models.CASCADE, related_name='memberships'
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


class Tag(models.Model):
    tag = models.BinaryField()
    name = models.CharField(blank=True)
    owner = models.ForeignKey(
        'Person', blank=True, null=True, on_delete=models.CASCADE, related_name='tags'
    )

    def is_claimed(self):
        return self.owner is not None

    def binary_id(self):
        return self.tag.hex().upper()

    def __str__(self):
        n = self.name
        if not n:
            n = 'unnamed'
        if self.owner:
            n += f' ({self.owner})'
        return n


class Person(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'People'


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

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Tag


@receiver(post_save, sender=User)
def create_webui_tag(sender, instance, created, **kwargs):
    if created:
        if not Tag.objects.filter(owner=instance, name='WebUI').exists():
            Tag.objects.create(name='WebUI', owner=instance, tag='WebUI')

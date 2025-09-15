from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Scanner, Tag


class RegisterScanTests(TestCase):
    def test_register_thrice(self):
        user = User.objects.create(username='test', first_name='Test', last_name='User')
        scanner = Scanner.objects.create(id='scanner', name='Test Scanner')
        tag = Tag.objects.create(name='test', owner=user)
        tag_id = 'DEADBEEF'

        res = self.client.post(
            reverse('register_scan'),
            {'device_id': scanner.id, 'card_id': tag_id},
        )
        self.assertEqual(res.json()['state'], 'register')

        tag.refresh_from_db()
        self.assertEqual(tag.tag, tag_id)

        res = self.client.post(
            reverse('register_scan'),
            {'device_id': scanner.id, 'card_id': tag.tag},
        )
        self.assertEqual(res.json()['state'], 'checkin')

        res = self.client.post(
            reverse('register_scan'),
            {'device_id': scanner.id, 'card_id': tag.tag},
        )
        self.assertEqual(res.json()['state'], 'checkout')

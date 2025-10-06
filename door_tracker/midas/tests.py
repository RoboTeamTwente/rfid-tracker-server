from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .api import RegisterScanResponseSerializer
from .models import ClaimedTag, PendingTag, Scanner


class RegisterScanTests(TestCase):
    def test_register_thrice(self):
        user = User.objects.create(username='test', first_name='Test', last_name='User')
        scanner = Scanner.objects.create(id='scanner', name='Test Scanner')
        pending_tag = PendingTag.objects.create(
            name='test', owner=user, scanner=scanner
        )
        tag_code = 'DEADBEEF'

        def register_scan():
            response = self.client.post(
                reverse('midas:register_scan'),
                {'device_id': scanner.id, 'tag_id': tag_code},
            )
            json_response = response.json()
            print(f'{json_response=}')
            s = RegisterScanResponseSerializer(data=json_response)
            s.is_valid(raise_exception=True)
            return s.save()

        res = register_scan()
        self.assertEqual(res.state, 'register')
        self.assertEqual(res.owner_name, user.get_full_name())

        # after registration, a new claimed tag is created…
        claimed_tag = ClaimedTag.objects.filter(pk=tag_code).first()
        self.assertIsNotNone(claimed_tag)
        self.assertEqual(claimed_tag.name, pending_tag.name)
        self.assertEqual(claimed_tag.owner.id, pending_tag.owner.id)

        # …and the pending tag is deleted
        pending_tag = PendingTag.objects.filter(scanner=scanner).first()
        self.assertIsNone(pending_tag)

        for _ in range(10):
            # check in with the shiny new tag
            res = register_scan()
            self.assertEqual(res.state, 'checkin')
            self.assertEqual(res.owner_name, user.get_full_name())

            # and immediately check out
            res = register_scan()
            self.assertEqual(res.state, 'checkout')
            self.assertEqual(res.owner_name, user.get_full_name())

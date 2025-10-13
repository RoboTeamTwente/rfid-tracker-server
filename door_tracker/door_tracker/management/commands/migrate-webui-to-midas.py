import midas.models as m
import webui.models as w
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


def convert_log(cls, log, session):
    if log.tag.name == 'WebUI':
        log_type = m.LogType.REMOTE
        tag = None
    else:
        log_type = m.LogType.TAG
        tag = m.ClaimedTag.objects.get(code=log.tag.tag)

    return cls.objects.create(
        type=log_type,
        time=log.time,
        tag=tag,
        session=session,
    )


class Command(BaseCommand):
    def handle(self, *args, **options):
        # scrub the database
        m.Assignment.objects.all().delete()
        m.Checkin.objects.all().delete()
        m.Checkout.objects.all().delete()
        m.ClaimedTag.objects.all().delete()
        m.PendingTag.objects.all().delete()
        m.Quota.objects.all().delete()
        m.Scanner.objects.all().delete()
        m.Session.objects.all().delete()
        m.Subteam.objects.all().delete()

        # scanners
        m.Scanner.objects.bulk_create(
            m.Scanner(id=s.id, name=s.name) for s in w.Scanner.objects.all()
        )

        # tags
        m.ClaimedTag.objects.bulk_create(
            m.ClaimedTag(owner=tag.owner, name=tag.name, code=tag.tag)
            for tag in w.Tag.objects.all()
            if tag.name != 'WebUI' and tag.name != '' and tag.owner
        )

        # logs

        for user in User.objects.all():
            logs = list(
                w.Log.objects.order_by('time').filter(
                    tag__owner=user,
                    type__in=[
                        w.Log.LogEntryType.CHECKIN,
                        w.Log.LogEntryType.CHECKOUT,
                    ],
                )
            )
            for cin, cout in zip(logs[::2], logs[1::2]):
                assert cin.type == w.Log.LogEntryType.CHECKIN
                assert cout.type == w.Log.LogEntryType.CHECKOUT
                print(user, cin, cout, sep='\t')
                session = m.Session.objects.create(user=cin.tag.owner)
                convert_log(m.Checkin, cin, session)
                convert_log(m.Checkout, cout, session)

            if len(logs) % 2 == 1:
                cin = logs[-1]
                assert cin.type == w.Log.LogEntryType.CHECKIN
                print(user, cin, '-', sep='\t')
                session = m.Session.objects.create(user=cin.tag.owner)
                convert_log(m.Checkin, cin, session)

        # memberhips

        m.Subteam.objects.bulk_create(
            m.Subteam(name=s.name) for s in w.SubTeam.objects.all()
        )
        m.Quota.objects.bulk_create(
            m.Quota(name=j.name, hours=j.quota) for j in w.Job.objects.all()
        )
        for x in w.Membership.objects.all():
            a = m.Assignment.objects.create(
                user=x.person,
                quota=m.Quota.objects.get(name=x.job.name),
                starting_from=x.starting_from,
            )
            if x.subteam:
                a.subteams.set([m.Subteam.objects.get(name=x.subteam.name)])

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from mailing.models import Mailing, Attempt


class Command(BaseCommand):
    help = 'Отправляет активные рассылки'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status='started'
        )

        for mailing in mailings:
            self.send_mailing(mailing)

    def send_mailing(self, mailing):
        for client in mailing.recipients.all():
            try:
                send_mail(
                    mailing.message.subject,
                    mailing.message.body,
                    settings.DEFAULT_FROM_EMAIL,
                    [client.email],
                )
                Attempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status='success',
                    server_response='OK'
                )
                self.stdout.write(self.style.SUCCESS(f'Отправлено: {client.email}'))
            except Exception as e:
                Attempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status='failed',
                    server_response=str(e)
                )
                self.stdout.write(self.style.ERROR(f'Ошибка: {client.email} - {e}'))

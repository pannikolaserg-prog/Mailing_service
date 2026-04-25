from django.core.management.base import BaseCommand, CommandError
from mailing.models import Mailing
from mailing.utils import send_mailing


class Command(BaseCommand):
    help = 'Отправка рассылки по ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки для отправки')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']

        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID {mailing_id} не найдена')

        if mailing.status == 'completed':
            self.stdout.write(
                self.style.WARNING(f'Рассылка #{mailing_id} уже завершена')
            )
            return

        self.stdout.write(f'Начинаю отправку рассылки #{mailing_id}...')
        success, failure = send_mailing(mailing)

        self.stdout.write(
            self.style.SUCCESS(
                f'Отправка завершена! Успешно: {success}, Ошибок: {failure}'
            )
        )

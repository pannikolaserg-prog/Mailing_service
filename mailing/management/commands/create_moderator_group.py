from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Mailing


class Command(BaseCommand):
    help = 'Создает группу "Менеджер"'

    def handle(self, *args, **options):
        ct = ContentType.objects.get_for_model(Mailing)

        # Права
        can_view_all, _ = Permission.objects.get_or_create(
            codename='can_view_all_mailings',
            name='Может просматривать все рассылки',
            content_type=ct,
        )
        can_disable, _ = Permission.objects.get_or_create(
            codename='can_disable_mailing',
            name='Может отключать рассылки',
            content_type=ct,
        )

        # Группа
        group, _ = Group.objects.get_or_create(name='Менеджер')
        group.permissions.add(can_view_all, can_disable)

        self.stdout.write(self.style.SUCCESS('Группа "Менеджер" создана'))

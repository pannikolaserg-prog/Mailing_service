from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Client, Message, Mailing


class Command(BaseCommand):
    help = 'Создает группы пользователей'

    def handle(self, *args, **options):
        # Менеджеры
        manager_group, _ = Group.objects.get_or_create(name='Менеджер')

        content_types = [
            ContentType.objects.get_for_model(Client),
            ContentType.objects.get_for_model(Message),
            ContentType.objects.get_for_model(Mailing),
        ]

        for ct in content_types:
            perms = Permission.objects.filter(content_type=ct)
            manager_group.permissions.add(*perms)

        self.stdout.write(self.style.SUCCESS('Группы созданы'))

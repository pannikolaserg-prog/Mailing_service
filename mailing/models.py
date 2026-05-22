from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.email


class Message(models.Model):
    subject = models.CharField(max_length=200)
    body = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS, default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Client)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def update_status(self):
        now = timezone.now()
        if now < self.start_time:
            self.status = 'created'
        elif now <= self.end_time:
            self.status = 'started'
        else:
            self.status = 'completed'
        self.save(update_fields=['status'])

    def send_batch(self):
        from django.core.mail import send_mail
        from django.conf import settings
        from .models import Attempt

        attempts = []
        for client in self.recipients.all():
            try:
                send_mail(
                    self.message.subject,
                    self.message.body,
                    settings.DEFAULT_FROM_EMAIL,
                    [client.email],
                )
                attempts.append(Attempt(
                    mailing=self,
                    client=client,
                    status='success',
                    server_response='OK'
                ))
            except Exception as e:
                attempts.append(Attempt(
                    mailing=self,
                    client=client,
                    status='failed',
                    server_response=str(e)
                ))

        # Batch create
        Attempt.objects.bulk_create(attempts)
        return len(attempts)


class Attempt(models.Model):
    STATUS = [('success', 'Успешно'), ('failed', 'Ошибка')]
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS)
    server_response = models.TextField(blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True,)

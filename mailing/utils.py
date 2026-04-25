from django.core.mail import send_mail
from django.conf import settings
from .models import Attempt
import logging

logger = logging.getLogger(__name__)


def send_mailing(mailing):
    """
    Отправка рассылки всем получателям
    Возвращает кортеж (успешно, не успешно)
    """
    success_count = 0
    failure_count = 0

    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            Attempt.objects.create(
                status='success',
                server_response='OK - письмо успешно отправлено',
                mailing=mailing
            )
            success_count += 1
            logger.info(f'Письмо отправлено {recipient.email} для рассылки #{mailing.pk}')

        except Exception as e:
            error_message = str(e)
            Attempt.objects.create(
                status='failure',
                server_response=error_message,
                mailing=mailing
            )
            failure_count += 1
            logger.error(f'Ошибка отправки {recipient.email}: {error_message}')

    # Обновляем статус рассылки после отправки
    mailing.update_status()

    return success_count, failure_count

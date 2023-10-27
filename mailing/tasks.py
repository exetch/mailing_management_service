from typing import Tuple

from django.core.mail import send_mail
from django.db.models import Q

from clients.models import Client
from .models import Mailing, Message
from logs.models import MailingLog
from django.utils import timezone
from django.conf import settings
import schedule
import time
from datetime import timedelta, datetime
from pytz import timezone as tz


def send_email_to_client(subject: str, message: str, client_email: str) -> Tuple[str, str]:
    """
    Отправляет электронное письмо клиенту.

    :param subject: Тема сообщения.
    :param message: Текст сообщения.
    :param client_email: Адрес электронной почты клиента.
    :return: Кортеж, содержащий статус отправки и ответ сервера.
    """
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [client_email],
            fail_silently=False
        )
        return 'sent', 'Email sent successfully'
    except Exception as e:
        return 'error', str(e)

def log_email_status(mailing: Mailing, client: Client, status: str, server_response: str) -> None:
    """
    Логирует статус отправленного электронного письма.

    :param mailing: Объект рассылки.
    :param client: Объект клиента.
    :param status: Статус отправки ('sent', 'error').
    :param server_response: Ответ сервера или описание ошибки.
    """
    MailingLog.objects.create(
        mailing=mailing,
        client=client,
        sent_datetime=timezone.now(),
        status=status,
        server_response=server_response
    )


def send_emails() -> None:
    """
    Отправляет электронные письма согласно установленному расписанию и статусу рассылки.

    Проходит через все рассылки и проверяет, пора ли отправить следующее письмо.
    Отправляет письма всем клиентам, подписанным на рассылку.
    """
    current_time = timezone.now().time()

    now = timezone.now()
    mailings = Mailing.objects.filter(
        Q(start_date__lte=now) | Q(start_date__isnull=True),
        Q(end_date__gte=now) | Q(end_date__isnull=True)
    ).filter(Q(status='created') | (Q(status='started') & Q(send_time__lte=current_time)))
    for mailing in mailings:

        if is_time_to_send(mailing):
            clients = mailing.clients.all()
            message = Message.objects.get(mailing=mailing)

            for client in clients:
                status, server_response = send_email_to_client(message.subject, message.body, client.email)
                log_email_status(mailing, client, status, server_response)
                if mailing.status == 'created':
                    mailing.status = 'started'
                    mailing.save()

def is_time_to_send(mailing: Mailing) -> bool:
    """
    Определяет, пора ли отправить следующее письмо в рассылке.

    :param mailing: Объект рассылки.
    :return: True, если пора отправить письмо, иначе False.
    """
    moscow_tz = tz('Europe/Moscow')
    send_time = moscow_tz.localize(datetime.combine(datetime.now().date(), mailing.send_time))

    # Обработка для рассылок со статусом "created"
    if mailing.status == 'created':
        return send_time <= moscow_tz.localize(datetime.now())

    # Обработка для рассылок со статусом "started"
    elif mailing.status == 'started':
        try:
            last_log_entry = MailingLog.objects.filter(mailing=mailing).latest('sent_datetime')

            if mailing.send_frequency == 'daily':
                period = timedelta(days=1)
            elif mailing.send_frequency == 'weekly':
                period = timedelta(weeks=1)
            elif mailing.send_frequency == 'monthly':
                period = timedelta(days=30)

            return last_log_entry.sent_datetime + period <= moscow_tz.localize(datetime.now()) and send_time <= moscow_tz.localize(datetime.now())
        except MailingLog.DoesNotExist:
            return False


def resend_failed_emails() -> None:
    """
    Повторно отправляет электронные письма, которые не удалось отправить ранее.

    Перебирает все логи с ошибками и проверяет, является ли последняя запись в логе ошибкой.
    Если это так, повторно отправляет письмо.
    """
    error_logs = MailingLog.objects.filter(status='error')

    checked_combinations = set()

    for error_log in error_logs:
        mailing = error_log.mailing
        client = error_log.client
        if (mailing.id, client.id) in checked_combinations:
            continue
        checked_combinations.add((mailing.id, client.id))
        try:
            last_log_entry = MailingLog.objects.filter(mailing=mailing, client=client).latest('sent_datetime')
            if last_log_entry.status == 'error':
                message = Message.objects.get(mailing=mailing)
                status, server_response = send_email_to_client(message.subject, message.body, client.email)
                log_email_status(mailing, client, status, server_response)
        except MailingLog.DoesNotExist:
            continue

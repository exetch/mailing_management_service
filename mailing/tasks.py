from django.core.mail import send_mail
from django.db.models import Q
from .models import Mailing, Message
from logs.models import MailingLog
from django.utils import timezone
from django.conf import settings
import schedule
import time
from datetime import timedelta, datetime
from pytz import timezone as tz


def send_email_to_client(subject, message, client_email):
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

def log_email_status(mailing, client, status, server_response):
    MailingLog.objects.create(
        mailing=mailing,
        client=client,
        sent_datetime=timezone.now(),
        status=status,
        server_response=server_response
    )

def send_emails():
    current_time = timezone.now().time()
    # mailings = Mailing.objects.filter(Q(status='created') | (Q(status='started') & Q(send_time__lte=current_time)))

    now = timezone.now()
    mailings_to_send = Mailing.objects.filter(
        Q(start_date__lte=now) | Q(start_date__isnull=True),
        Q(end_date__gte=now) | Q(end_date__isnull=True)
    ).filter(Q(status='created') | (Q(status='started') & Q(send_time__lte=current_time)))

    for mailing in mailings_to_send:
        if mailing.end_date and mailing.end_date < now:
            mailing.status = 'completed'
            mailing.save()
            continue

        if is_time_to_send(mailing):
            clients = mailing.clients.all()
            message = Message.objects.get(mailing=mailing)

            for client in clients:
                status, server_response = send_email_to_client(message.subject, message.body, client.email)
                log_email_status(mailing, client, status, server_response)
                if mailing.status == 'created':
                    mailing.status = 'started'
                    mailing.save()

def is_time_to_send(mailing):
    try:
        last_log_entry = MailingLog.objects.filter(mailing=mailing).latest('sent_datetime')
        send_time = tz('Europe/Moscow').localize(datetime.combine(timezone.now().date(), mailing.send_time))
        if mailing.status == 'created':
            return send_time <= timezone.now()
        elif mailing.status == 'started':
            if mailing.send_frequency == 'daily':
                period = timedelta(days=1)
            elif mailing.send_frequency == 'weekly':
                period = timedelta(weeks=1)
            elif mailing.send_frequency == 'monthly':
                period = timedelta(days=30)
            return last_log_entry.sent_datetime + period <= timezone.now() and send_time <= timezone.now()
    except MailingLog.DoesNotExist:
        return False


def run_mailing():
    send_emails()
    schedule.every(5).minutes.do(send_emails)

    while True:
        schedule.run_pending()
        time.sleep(60)
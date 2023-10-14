from django.core.mail import send_mail
from .models import Mailing, Message
from clients.models import Client
from logs.models import MailingLog
from django.utils import timezone
from django.conf import settings
import schedule
import time


def send_emails():
    current_time = timezone.now().time()
    current_date = timezone.now().date()

    mailings = Mailing.objects.filter(status='created')

    for mailing in mailings:
        clients = Client.objects.all()
        message = Message.objects.get(mailing=mailing)
        for client in clients:
            try:
                send_mail(
                    message.subject,
                    message.body,
                    settings.EMAIL_HOST_USER,
                    [client.email],
                    fail_silently=False
                )
                status = 'sent'
                server_response = 'Email sent successfully'
            except Exception as e:
                status = 'error'
                server_response = str(e)

            MailingLog.objects.create(
                mailing=mailing,
                client=client,
                sent_datetime=timezone.now(),
                status=status,
                server_response=server_response
            )

        # mailing.status = 'completed'
        mailing.save()
    print("отправка завершена")
def run_mailing():

    schedule.every(2).minutes.do(send_emails)

    while True:
        schedule.run_pending()
        time.sleep(1)
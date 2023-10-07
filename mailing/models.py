from django.db import models
from django.utils import timezone

class Client(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

class Mailing(models.Model):
    SEND_CHOICES = (
        ('daily', 'Раз в день'),
        ('weekly', 'Раз в неделю'),
        ('monthly', 'Раз в месяц'),
    )
    send_time = models.TimeField()
    send_frequency = models.CharField(max_length=10, choices=SEND_CHOICES)
    status = models.CharField(max_length=10, default='created')

class MailingLog(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sent_datetime = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20)
    server_response = models.TextField(blank=True)

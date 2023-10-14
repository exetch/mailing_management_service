from django.db import models
from clients.models import Client

NULLABLE = {'null': True, 'blank': True}

class Mailing(models.Model):
    SEND_CHOICES = (
        ('daily', 'раз в день'),
        ('weekly', 'раз в неделю'),
        ('monthly', 'раз в месяц'),
    )
    STATUS_CHOICES = (
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    )
    send_time = models.TimeField(verbose_name="Время рассылки")
    send_frequency = models.CharField(max_length=10, choices=SEND_CHOICES, verbose_name="Частота рассылки")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='created', verbose_name="Статус рассылки")
    clients = models.ManyToManyField(Client, verbose_name="Клиенты", related_name="mailings", **NULLABLE)

    def __str__(self):
        return f"{self.send_time} {self.send_frequency}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема')
    body = models.TextField(verbose_name='Сообщение')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, **NULLABLE, verbose_name='Рассылка')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


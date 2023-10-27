from django.db import models
from django.utils import timezone


NULLABLE = {'null': True, 'blank': True}
class MailingLog(models.Model):
    mailing = models.ForeignKey('mailing.Mailing', on_delete=models.CASCADE)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    sent_datetime = models.DateTimeField(auto_now=True, verbose_name="Дата и время последней попытки отправки")
    status = models.CharField(max_length=20)
    server_response = models.TextField(**NULLABLE)
    error_type = models.CharField(max_length=50, **NULLABLE)

    def __str__(self):
        return f"Лог {self.id}"

    class Meta:
        verbose_name = "Лог"
        verbose_name_plural = "Логи"
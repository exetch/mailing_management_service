from django.db import models

NULLABLE = {'null': True, 'blank': True}

class Client(models.Model):
    email = models.EmailField(verbose_name="email")
    full_name = models.CharField(max_length=255, verbose_name="Клиент")
    comment = models.TextField(**NULLABLE, verbose_name="Комментарий")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

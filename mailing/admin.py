from django.contrib import admin
from .models import Mailing, Client, Message, MailingLog


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'send_time', 'send_frequency', 'status')
    list_filter = ('send_frequency', 'status')
    search_fields = ('id', 'status')
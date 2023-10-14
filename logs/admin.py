from django.contrib import admin
from .models import MailingLog


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'client', 'sent_datetime', 'status', 'server_response')
    list_filter = ('mailing', 'client', 'status', 'sent_datetime', 'server_response')
    search_fields = ('mailing', 'client', 'status', 'sent_datetime', 'server_response')
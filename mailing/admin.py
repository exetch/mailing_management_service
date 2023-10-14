from django.contrib import admin
from .models import Mailing, Message


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'send_time', 'send_frequency', 'status')
    list_filter = ('send_frequency', 'status')
    search_fields = ('id', 'status')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'body', 'mailing')
    list_filter = ('subject',)
    search_fields = ('subject', 'body')

from django.views.generic import ListView
from .models import MailingLog

class MailingLogListView(ListView):
    model = MailingLog
    template_name = 'logs/log_list.html'
    context_object_name = 'logs'



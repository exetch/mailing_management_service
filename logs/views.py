from django.views.generic import ListView
from .models import MailingLog
from django.contrib.auth.mixins import LoginRequiredMixin

class MailingLogListView(LoginRequiredMixin, ListView):
    model = MailingLog
    template_name = 'logs/log_list.html'
    context_object_name = 'logs'

    def get_queryset(self):
        queryset = super().get_queryset().filter(client__user=self.request.user)
        return queryset



from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Mailing

class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'

class MailingCreateView(CreateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    fields = ['send_time', 'send_frequency']

class MailingUpdateView(UpdateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    fields = ['send_time', 'send_frequency']

class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing-list')

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Mailing, Message
from clients.models import Client
from django.shortcuts import redirect
from django import forms

class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

class MailingCreateView(CreateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    fields = ['send_time', 'send_frequency']
    success_url = reverse_lazy('message_create')

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.status = 'created'
        mailing.save()
        return super().form_valid(form)

class MailingUpdateView(UpdateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    fields = ['send_time', 'send_frequency']
    success_url = reverse_lazy('mailing_list')

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.status = 'created'
        mailing.save()
        return super().form_valid(form)

class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

class MessageListView(ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

class MessageCreateView(CreateView):
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body', 'mailing']

    def form_valid(self, form):
        mailing = form.cleaned_data['mailing']
        mailing.save()
        mailing_id = mailing.id

        self.success_url = reverse_lazy('add_clients_to_mailing', kwargs={'mailing_id': mailing_id})

        return super().form_valid(form)

class MessageUpdateView(UpdateView):
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body', 'mailing']
    success_url = reverse_lazy('message_list')

class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('message_list')

class AddClientsToMailingView(TemplateView):
    template_name = 'mailing/add_clients_to_mailing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_id'] = self.kwargs['mailing_id']
        context['clients'] = Client.objects.all()  # Query all clients
        return context

    def post(self, request, mailing_id):
        selected_clients = request.POST.getlist('clients')
        mailing = Mailing.objects.get(pk=mailing_id)
        mailing.clients.add(*selected_clients)
        return redirect('mailing_list')


from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy

from .forms import MailingForm, MessageForm
from .models import Mailing, Message
from clients.models import Client
from django.shortcuts import redirect
from django import forms

class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()
        context['message'] = Message.objects.get(mailing=mailing)
        return context

class MailingCreateView(CreateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm
    success_url = reverse_lazy('message_create')

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.status = 'created'
        mailing.save()
        self.request.session['mailing_id'] = mailing.id
        return super().form_valid(form)

class MailingUpdateView(UpdateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm

    def get_success_url(self):
        return reverse_lazy('mailing_detail', kwargs={'pk': self.object.id})

class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

# class MessageListView(ListView):
#     model = Message
#     template_name = 'mailing/message_list.html'
#     context_object_name = 'messages'

class MessageCreateView(CreateView):
    model = Message
    template_name = 'mailing/message_form.html'
    form_class = MessageForm

    def form_valid(self, form):
        mailing_id = self.request.session.get('mailing_id')
        if mailing_id:
            mailing = Mailing.objects.get(id=mailing_id)
            form.instance.mailing = mailing
        mailing.save()
        mailing_id = mailing.id

        self.success_url = reverse_lazy('add_clients_to_mailing', kwargs={'pk': mailing_id})

        return super().form_valid(form)

class MessageUpdateView(UpdateView):
    model = Message
    template_name = 'mailing/message_form.html'
    form_class = MessageForm
    def form_valid(self, form):
        mailing = self.object.mailing

        self.success_url = reverse_lazy('mailing_detail', kwargs={'pk': mailing.id})

        return super().form_valid(form)

class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('message_list')


class AddClientsToMailingView(TemplateView):
    template_name = 'mailing/add_clients_to_mailing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing_id = self.kwargs['pk']
        mailing = Mailing.objects.get(pk=mailing_id)
        search_query = self.request.GET.get('search', '')

        context['mailing_id'] = mailing_id
        context['selected_clients'] = mailing.clients.all()

        query = Q(full_name__icontains=search_query) | Q(email__icontains=search_query)
        context['clients'] = Client.objects.filter(query)

        return context

    def post(self, request, *args, **kwargs):
        mailing_id = self.kwargs.get('pk')
        selected_clients = request.POST.getlist('clients')
        mailing = Mailing.objects.get(pk=mailing_id)
        mailing.clients.clear()
        mailing.clients.add(*selected_clients)
        return redirect('mailing_list')



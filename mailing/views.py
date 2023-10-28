from django.db.models import Q
from django.http import Http404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy

from .forms import MailingForm, MessageForm
from .models import Mailing, Message
from clients.models import Client
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()
        context['message'] = Message.objects.get(mailing=mailing)
        return context

class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm
    success_url = reverse_lazy('message_create')

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.status = 'created'
        mailing.user = self.request.user
        mailing.save()
        self.request.session['mailing_id'] = mailing.id
        return super().form_valid(form)

class MailingUpdateView(UpdateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """
        Переопределение метода dispatch для проверки, имеет ли пользователь право редактировать эту рассылку.
        """
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не имеете права редактировать эту рассылку.")
        return super(MailingUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('mailing_detail', kwargs={'pk': self.object.id})

class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
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

    def get_queryset(self):
        return super().get_queryset().filter(mailing__user=self.request.user)
    def form_valid(self, form):
        mailing = self.object.mailing

        self.success_url = reverse_lazy('mailing_detail', kwargs={'pk': mailing.id})

        return super().form_valid(form)

class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('message_list')

    def get_queryset(self):
        return super().get_queryset().filter(mailing__user=self.request.user)


class AddClientsToMailingView(TemplateView):
    template_name = 'mailing/add_clients_to_mailing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing_id = self.kwargs['pk']

        mailing = get_object_or_404(Mailing, pk=mailing_id, user=self.request.user)

        search_query = self.request.GET.get('search', '')

        context['mailing_id'] = mailing_id
        context['selected_clients'] = mailing.clients.all()

        query = Q(full_name__icontains=search_query) | Q(email__icontains=search_query)

        context['clients'] = Client.objects.filter(query, user=self.request.user)

        return context

    def post(self, request, *args, **kwargs):
        mailing_id = self.kwargs.get('pk')

        mailing = get_object_or_404(Mailing, pk=mailing_id, user=self.request.user)

        selected_clients = request.POST.getlist('clients')

        mailing.clients.clear()
        mailing.clients.add(*Client.objects.filter(id__in=selected_clients, user=self.request.user))

        return redirect('mailing_list')



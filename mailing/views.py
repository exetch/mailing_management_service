from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import MailingForm, MessageForm
from .models import Mailing, Message
from clients.models import Client
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user

        cache_key = f'mailings_for_user_{user.id}'

        cached_queryset = cache.get(cache_key)

        if cached_queryset is not None:
            return cached_queryset
        else:
            if user.groups.filter(name='Менеджер').exists():
                queryset = super().get_queryset()
            else:
                queryset = super().get_queryset().filter(user=user)
            cache.set(cache_key, queryset, 60)

            return queryset


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()
        context['message'] = Message.objects.get(mailing=mailing)
        return context


class MailingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'mailing.add_mailing'
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


class MailingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'mailing.change_mailing'
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('mailing_detail', kwargs={'pk': self.object.id})


class MailingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'mailing.delete_mailing'
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class MessageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'mailing.add_message'
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
        self.request.session['current_stage'] = 'add_clients'
        self.success_url = reverse_lazy('add_clients_to_mailing', kwargs={'pk': mailing_id})

        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'mailing.change_message'
    model = Message
    template_name = 'mailing/message_form.html'
    form_class = MessageForm

    def get_queryset(self):
        return super().get_queryset().filter(mailing__user=self.request.user)

    def form_valid(self, form):
        mailing = self.object.mailing

        self.success_url = reverse_lazy('mailing_detail', kwargs={'pk': mailing.id})

        return super().form_valid(form)


class AddClientsToMailingView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'mailing.change_mailing'
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


@login_required
def complete_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if request.user.groups.filter(name='Менеджер').exists():
        mailing.status = 'completed'
        mailing.save()
        messages.success(request, 'Рассылка завершена.')
    else:
        messages.error(request, 'У вас нет прав на выполнение этой операции.')

    return redirect(reverse_lazy('mailing_detail', args=[pk]))

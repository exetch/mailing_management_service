from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Client
from .forms import ClientForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache

class ClientsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'clients.view_client'
    model = Client
    template_name = 'clients/clients_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        user_id = self.request.user.id
        cache_key = f'filtered_clients_{user_id}'

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        queryset = super().get_queryset().filter(user=self.request.user)

        cache.set(cache_key, queryset, 60)

        return queryset

class ClientsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'clients.add_client'
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('clients_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super(ClientsCreateView, self).form_valid(form)

        next_url = self.request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return response

class ClientsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'clients.change_client'
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('clients_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ClientsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'clients.delete_client'
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Client
from django.urls import reverse_lazy
class ClientsListView(ListView):
    model = Client
    template_name = 'clients/clients_list.html'
    context_object_name = 'clients'

class ClientsCreateView(CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['email', 'full_name', 'comment']

    def get_success_url(self):
        return reverse_lazy('clients_list')

class ClientsUpdateView(UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['email', 'full_name', 'comment']

    def get_success_url(self):
        return reverse_lazy('clients_list')

class ClientsDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('clients_list')

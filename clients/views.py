from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Client
from .forms import ClientForm
from django.contrib.auth.mixins import LoginRequiredMixin

class ClientsListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/clients_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class ClientsCreateView(LoginRequiredMixin, CreateView):
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

class ClientsUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('clients_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """
        Переопределение метода dispatch для проверки, имеет ли пользователь право редактировать этого клиента.
        """
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не имеете права редактировать этого клиента.")
        return super(ClientsUpdateView, self).dispatch(request, *args, **kwargs)

class ClientsDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

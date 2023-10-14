from django.urls import path
from . import views

urlpatterns = [
    path('clients/', views.ClientsListView.as_view(), name='clients_list'),
    path('clients/create/', views.ClientsCreateView.as_view(), name='client_form'),
    path('clients/<int:pk>/update/', views.ClientsUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientsDeleteView.as_view(), name='client_delete'),
]
from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailing/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/update/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailing/add_clients/<int:pk>/', views.AddClientsToMailingView.as_view(), name='add_clients_to_mailing'),
    path('message/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/update/', views.MessageUpdateView.as_view(), name='message_update'),
    path('complete_mailing/<int:pk>/', views.complete_mailing, name='complete_mailing'),
]
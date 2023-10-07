from django.urls import path
from . import views

urlpatterns = [
    path('mailing/', views.MailingListView.as_view(), name='mailing_list'),
]
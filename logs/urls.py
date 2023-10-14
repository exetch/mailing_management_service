from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.MailingLogListView.as_view(), name='log_list'),
]
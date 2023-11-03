from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('logs/', cache_page(60)(views.MailingLogListView.as_view()), name='log_list'),
]
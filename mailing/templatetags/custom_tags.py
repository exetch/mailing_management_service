from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='is_manager')
def is_manager(user):
    return user.groups.filter(name='Менеджер').exists()
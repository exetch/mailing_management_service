from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Создание групп пользователей и назначение прав'

    def handle(self, *args, **options):
        regular_user_group, _ = Group.objects.get_or_create(name='Обычный пользователь')
        self.assign_permissions(regular_user_group, {
            'blog': ['view_blogpost'],
            'mailing': ['view_mailing', 'add_mailing', 'change_mailing', 'delete_mailing', 'view_message', 'add_message', 'change_message', 'delete_message'],
            'clients': ['view_client', 'add_client', 'change_client', 'delete_client'],
            'logs': ['view_mailinglog'],
        })
        manager_group, _ = Group.objects.get_or_create(name='Менеджер')
        self.assign_permissions(manager_group, {
            'blog': ['view_blogpost', 'add_blogpost', 'change_blogpost', 'delete_blogpost'],
            'mailing': ['view_mailing', 'view_message'],
            'users': ['view_customuser'],
        })

        print('Группы пользователей и права успешно созданы')

    def assign_permissions(self, group, permissions):
        for app_label, perm_codenames in permissions.items():
            for codename in perm_codenames:
                model = codename.split('_')[1]
                model = model.lower()
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                permission = Permission.objects.get(codename=codename, content_type=content_type)
                group.permissions.add(permission)

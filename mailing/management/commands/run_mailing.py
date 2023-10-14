from django.core.management.base import BaseCommand
from mailing.tasks import run_mailing

class Command(BaseCommand):
    help = 'Send periodic emails'

    def handle(self, *args, **options):
        run_mailing()
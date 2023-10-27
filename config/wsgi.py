"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from apscheduler.schedulers.background import BackgroundScheduler
from mailing.tasks import send_emails

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

scheduler = BackgroundScheduler()
scheduler.add_job(send_emails, 'interval', minutes=2)
scheduler.start()
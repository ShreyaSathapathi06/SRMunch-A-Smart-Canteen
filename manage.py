#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_canteen.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

from django.contrib.auth.models import User
from accounts.models import StudentProfile

for u in User.objects.all():
    StudentProfile.objects.get_or_create(
        user=u,
        defaults={'full_name': u.username.split('@')[0]}
    )
from canteen.models import Order, generate_order_id

for o in Order.objects.filter(order_id__isnull=True):
    o.order_id = generate_order_id()
    o.save()

for o in Order.objects.filter(order_id=""):
    o.order_id = generate_order_id()
    o.save()

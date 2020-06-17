from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.db.models import F

from insane_app.models import Profile

@shared_task
def increment_sanity(**kwargs):
    Profile.objects.filter(
        sanity__lt = F('rank__sanity_cap')
    ).update(sanity = F('sanity') + 1)

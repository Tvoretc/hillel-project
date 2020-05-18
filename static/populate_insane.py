import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beta_project.settings')

import django
django.setup()

import random
from insane_app.models import *
from faker import Faker

fake_gen = Faker()
sanity_ranks = {'Noobie': 10, 'Adept': 20, 'Fanatic': 40, 'Insanion': 80}

def create_ranks():
    for rank in sanity_ranks:
        r = SanityRank.objects.get_or_create(name=rank.key, sanity_cap=rank.value)
        r.save()

def populate(N=5):
    for entry in range(N):
        

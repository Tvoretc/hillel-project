# use fixtures instead

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beta_project.settings')

import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from insane_app.models import *
import random
from faker import Faker

fake_gen = Faker()


def create_ranks():
    ranks = {'noobie': 12, 'adept': 25, 'madman': 50, 'insanion': 100}
    for name in ranks:
        SanityRank.objects.get_or_create(name=name, defaults={'sanity_cap':ranks[name]})


def populate(N_user=16, N_story=20):
    create_ranks()

    while N_user > User.objects.count():
        email = fake_gen.email()

        try:
            User.objects.get(username=email.split('@')[0])
        except ObjectDoesNotExist:
            user = User.objects.create_user(
                first_name=fake_gen.name().split()[0],
                last_name=fake_gen.name().split()[1],
                username=email.split('@')[0],
                password='default',
                email=email
            )

    #
    #     for i in range(N_user - Membership.objects.count()):
    #         if(i % 4 == 0):
    #             group = UserGroup.objects.get_or_create(name=fake_gen.company())
    #             Membership.objects.get_or_create(
    #             user=user,
    #             user_group=group,
    #             role=Membership.ROLES[0][0]
    #             )
    #         else:
    #             group = UserGroup.objects.get(
    #             random.randint(0, UserGroup.objects.count() - 1)
    #             )
    #         Membership.objects.get_or_create(
    #             user=user,
    #             user_group=group,
    #             role=Membership.ROLES[1][0]
    #         )
    #
    # for i in range(N_story):
    #     Story.objects.get_or_create(
    #         name=fake_gen.name(),
    #         body=fake_gen.text(),
    #         author=User.objects.get(random.randint(0, User.objects.count()-1))
    #     )




if __name__ == '__main__':
    print("populating...")
    populate()
    print("successfully populated.")

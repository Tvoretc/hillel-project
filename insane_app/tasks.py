# from celery import Celery
#
# # from insane_app.models import Profile
#
# app = Celery('tasks', backend='amqp', broker='amqp://')
#
# @app.task
# def increment_sanity_task(ignore_result=True):
#     print(f'1+1={2}')
#     # Profile.objects.filter(sanity__lt=F('rank.sanity_cap')).sanity = F('sanity') + 1
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task(ignore_result=True)
def print_hello():
    print('hello there')
    return 1;

# Generated by Django 3.0.3 on 2020-05-13 05:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insane_app', '0003_productcomment_productcommentlike_storycomment_storycommentlike'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='_sanity',
            new_name='sanity',
        ),
    ]

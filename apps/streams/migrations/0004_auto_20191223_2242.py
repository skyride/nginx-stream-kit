# Generated by Django 2.2.9 on 2019-12-23 22:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0003_auto_20191223_2239'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stream',
            old_name='stream_key',
            new_name='status',
        ),
    ]

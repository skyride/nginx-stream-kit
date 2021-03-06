# Generated by Django 2.2.9 on 2020-01-22 21:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.crypto
import functools


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(default=functools.partial(django.utils.crypto.get_random_string, *(16,), **{}), max_length=16, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stream_keys', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

# Generated by Django 2.2.9 on 2020-01-22 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0018_segment_file_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcodeprofile',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]

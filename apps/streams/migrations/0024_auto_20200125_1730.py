# Generated by Django 2.2.9 on 2020-01-25 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0023_auto_20200122_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcodeprofile',
            name='audio_codec',
            field=models.CharField(choices=[('libfdk_aac', 'AAC'), ('copy', 'Copy')], max_length=64),
        ),
    ]

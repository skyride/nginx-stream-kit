# Generated by Django 2.2.9 on 2020-01-21 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0016_auto_20200121_1929'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='duration',
            field=models.FloatField(default=5),
            preserve_default=False,
        ),
    ]

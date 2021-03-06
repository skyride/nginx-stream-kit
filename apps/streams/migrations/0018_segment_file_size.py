# Generated by Django 2.2.9 on 2020-01-22 21:01

from django.db import migrations, transaction
import sizefield.models

def populate_file_size_file(apps, schema_editor):
    Segment = apps.get_model("streams", "Segment")

    with transaction.atomic():
        for segment in Segment.objects.all():
            segment.file_size = segment.file.size
            segment.save()


def blank_backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0017_segment_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='file_size',
            field=sizefield.models.FileSizeField(default=0),
        ),
        migrations.RunPython(populate_file_size_file, blank_backwards),
        migrations.AlterField(
            model_name='segment',
            name='file_size',
            field=sizefield.models.FileSizeField(),
        ),
    ]

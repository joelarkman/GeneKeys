# Generated by Django 3.0.4 on 2020-04-08 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_transcript_use_by_default'),
    ]

    operations = [
        migrations.RenameField(
            model_name='panelgene',
            old_name='transcript',
            new_name='preferred_transcript',
        ),
    ]
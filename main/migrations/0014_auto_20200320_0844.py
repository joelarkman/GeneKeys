# Generated by Django 3.0.4 on 2020-03-20 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20200315_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genekey',
            name='gene_key',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='panel',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
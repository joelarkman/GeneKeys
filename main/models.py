from django.db import models
from django.db.models.deletion import SET_DEFAULT, SET_NULL
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User


class Panel(models.Model):
    name = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=100, blank=True)
    genes = models.ManyToManyField(
        'Gene', through='PanelGene', related_name='Panels')

    def __str__(self):
        return self.name


class Gene(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Transcript(models.Model):
    name = models.CharField(max_length=20, unique=True)
    Gene = models.ForeignKey(Gene, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PanelGene(models.Model):
    panel = models.ForeignKey(
        'panel', related_name='PanelGene', on_delete=models.SET_NULL, null=True)
    gene = models.ForeignKey('Gene', related_name='PanelGene',
                             on_delete=models.SET_NULL, null=True)
    transcript = models.ForeignKey(
        'Transcript', related_name='PrefferedTranscript', null=True, blank=True, on_delete=models.CASCADE)


class GeneKey(models.Model):
    panel = models.ForeignKey(
        'panel', related_name='GeneKey', on_delete=models.CASCADE)
    gene_key = models.CharField(max_length=10, unique=True)
    genes = models.ManyToManyField('Gene', related_name='gene_keys')
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        User, related_name='gene_keys', null=True, on_delete=SET_NULL)
    checked = models.BooleanField(default=False)
    checked_at = models.DateTimeField(null=True, blank=True)
    checked_by = models.ForeignKey(
        User, null=True, related_name='+', on_delete=SET_NULL, blank=True)
    archived = models.BooleanField(default=False)

    def gene_names(self):
        return ', '.join([gene.name for gene in self.genes.all()])
    gene_names.short_description = "Gene Names"

    def __str__(self):
        return self.gene_key

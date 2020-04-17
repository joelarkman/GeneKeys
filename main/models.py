from django.db import models
from django.db.models.deletion import SET_NULL
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User


class Panel(models.Model):
    name = models.CharField(max_length=10, unique=True)
    description = models.TextField(null=True, blank=True)
    genes = models.ManyToManyField(
        'Gene', through='PanelGene', related_name='Panels')

    # These fields are not editable and are defined automatically/using special admin class.
    # They would also not be visible within admin by default so are displayed as readonly using speacial admin class.
    added_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(
        User, related_name='panels', editable=False, null=True, on_delete=SET_NULL)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    modified_by = models.ForeignKey(
        User, null=True, related_name='+', editable=False, on_delete=SET_NULL, blank=True)

    def __str__(self):
        return self.name


class Gene(models.Model):
    name = models.CharField(max_length=10, unique=True)

    added_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(
        User, related_name='genes', editable=False, null=True, on_delete=SET_NULL)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    modified_by = models.ForeignKey(
        User, null=True, editable=False, related_name='+', on_delete=SET_NULL, blank=True)

    def __str__(self):
        return self.name


class Transcript(models.Model):
    name = models.CharField(max_length=20, unique=True)
    Gene = models.ForeignKey(
        Gene, on_delete=models.CASCADE, related_name='transcripts')
    use_by_default = models.BooleanField()

    added_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(
        User, related_name='transcripts', editable=False, null=True, on_delete=SET_NULL)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    modified_by = models.ForeignKey(
        User, null=True, editable=False, related_name='+', on_delete=SET_NULL, blank=True)

    def __str__(self):
        return self.name


class PanelGene(models.Model):
    panel = models.ForeignKey(
        'panel', related_name='PanelGene', on_delete=models.CASCADE, null=True)
    gene = models.ForeignKey('Gene', related_name='PanelGene',
                             on_delete=models.CASCADE, null=True, blank=True)
    preferred_transcript = models.ForeignKey(
        'Transcript', related_name='PrefferedTranscript', null=True, blank=True, on_delete=models.SET_NULL)

    added_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(
        User, related_name='panel_genes', editable=False, null=True, on_delete=SET_NULL)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    modified_by = models.ForeignKey(
        User, null=True, editable=False, related_name='+', on_delete=SET_NULL, blank=True)

    # Stop the same gene being added to a panel twice.
    class Meta:
        unique_together = ('panel', 'gene',)

    def active_keys(self):
        return ', '.join([key.key for key in self.gene.gene_keys.filter(panel=self.panel).exclude(checked=False).exclude(archived=True)])
    active_keys.short_description = "Active Keys"

    def __str__(self):
        return f'Panel: {self.panel}; Gene:  {self.gene}'


class GeneKey(models.Model):
    panel = models.ForeignKey(
        'panel', related_name='GeneKey', on_delete=models.CASCADE)
    key = models.CharField(max_length=20, unique=True)
    genes = models.ManyToManyField('Gene', related_name='gene_keys')
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        User, related_name='gene_keys', editable=False, null=True, on_delete=SET_NULL)
    checked = models.BooleanField(default=False)
    checked_at = models.DateTimeField(null=True, blank=True)
    checked_by = models.ForeignKey(
        User, null=True, related_name='+', on_delete=SET_NULL, blank=True)
    archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        User, null=True, related_name='+', on_delete=SET_NULL, blank=True)
    comment = models.TextField(null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True)
    modified_by = models.ForeignKey(
        User, null=True, editable=False, related_name='+', on_delete=SET_NULL, blank=True)

    def gene_names(self):
        return ', '.join([gene.name for gene in self.genes.all()])
    gene_names.short_description = "Gene Names"

    def __str__(self):
        return self.key

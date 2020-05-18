from django.test import TestCase
from mixer.backend.django import mixer
import pytest

from main.models import Panel, Gene, Transcript, PanelGene, GeneKey


@pytest.mark.django_db
class TestModels(TestCase):

    def setUp(self):
        self.panel = mixer.blend('main.Panel', name='Panel_1')
        self.gene = mixer.blend('main.Gene', name='Gene_1')
        self.transcript = mixer.blend('main.Transcript', name='Transcript_1')
        self.gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=True, genes=self.gene)
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene)

    def test_panel_creation(self):
        self.assertTrue(isinstance(self.panel, Panel))
        self.assertEqual(self.panel.__str__(), self.panel.name)

    def test_gene_creation(self):
        self.assertTrue(isinstance(self.gene, Gene))
        self.assertEqual(self.gene.__str__(), self.gene.name)

    def test_transcript_creation(self):
        self.assertTrue(isinstance(self.transcript, Transcript))
        self.assertEqual(self.transcript.__str__(), self.transcript.name)

    def test_PanelGene_creation(self):
        self.assertTrue(isinstance(self.panel_gene, PanelGene))
        self.assertEqual(self.panel_gene.__str__(),
                         'Panel: Panel_1; Gene: Gene_1')
        self.assertEqual(self.panel_gene.active_keys(), 'GeneKey_1')

    def test_GeneKey_creation(self):
        self.assertTrue(isinstance(self.gene_key, GeneKey))
        self.assertEqual(self.gene_key.__str__(), self.gene_key.key)
        self.assertEqual(self.gene_key.gene_names(), 'Gene_1')

from django.test import TestCase
from mixer.backend.django import mixer
from django.urls import resolve, reverse
import pytest

from main.models import Panel, Gene, GeneKey
from main.forms import AddKeyForm


@pytest.mark.django_db
class TestAddKeyForm(TestCase):

    # Define a panel and two genes, add one of the genes to the panel.
    def setUp(self):
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene_on_panel = mixer.blend('main.Gene', name='Gene_1')
        self.gene_not_on_panel = mixer.blend('main.Gene', name='Gene_2')
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene_on_panel)

    # Test the form is valid when a key is created which relates to a gene that is on the panel.
    def test_AddKey_form_valid_gene(self):
        form = AddKeyForm(data={
            'panel': self.panel.id,
            'key': 'Example_key_1',
            'genes': [self.gene_on_panel],
            'comment': 'example comment'
        })

        self.assertTrue(form.is_valid())

    # Test the form is invalid when a key is created which relates to a gene that is not on the panel.
    def test_AddKey_form_invalid_gene(self):
        form = AddKeyForm(data={
            'panel': self.panel.id,
            'key': 'Example_key_2',
            'genes': [self.gene_not_on_panel],
            'comment': 'example comment'
        })

        self.assertFalse(form.is_valid())

    #  Test the form is invalid when a valid panel is not provided.
    def test_AddKey_form_invalid_panel(self):
        form = AddKeyForm(data={
            'panel': 'incorrect_panel',
            'key': 'Example_key_2',
            'genes': [self.gene_on_panel],
            'comment': 'example comment'
        })

        self.assertFalse(form.is_valid())

    # Test a valid form correctly saves, the added object exists and its genes match to the provided input.
    def test_AddKey_form_save(self):
        form = AddKeyForm(data={
            'panel': self.panel.id,
            'key': 'Example_key_1',
            'genes': [self.gene_on_panel],
            'comment': 'example comment'
        })

        result = form.save()

        saved_object = list(GeneKey.objects.get(
            key='Example_key_1').genes.all())

        self.assertEqual(form.data['genes'], saved_object)

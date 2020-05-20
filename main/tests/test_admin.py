from django.test import TestCase, Client, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from mixer.backend.django import mixer

import pytest

from main.models import Panel, Gene, Transcript, PanelGene, GeneKey
from main.admin import AddPanelGeneInline, PanelAdmin, GeneAdmin, GeneKeyAdmin


class MockRequest(object):
    def __init__(self, user=None):
        self.user = user


class TestAddPanelGeneInline(TestCase):
    def setUp(self):
        self.panel_gene_admin = AddPanelGeneInline(
            parent_model=PanelGene, admin_site=AdminSite())
        self.super_user = User.objects.create_superuser(username='super', email='super@email.org',
                                                        password='pass')

    def test_add_panel_gene_in_line_get_queryset_returns_empty_queryset(self):
        get_queryset1 = self.panel_gene_admin.get_queryset(
            request=MockRequest(user=self.super_user))

        self.assertQuerysetEqual(
            get_queryset1, PanelGene.objects.none())


@pytest.mark.django_db
class TestPanelAdmin(TestCase):
    def setUp(self):
        self.panel_admin = PanelAdmin(model=Panel, admin_site=AdminSite())
        self.super_user = User.objects.create_superuser(username='super', email='super@email.org',
                                                        password='pass')

        self.panel = mixer.blend('main.Panel', name='PANEL_1', added_by=None)

    def test_save_panel_model(self):
        self.panel_admin.save_model(obj=self.panel, request=MockRequest(
            user=self.super_user), form=None, change=None)

        self.assertEqual(
            Panel.objects.get(id=1).added_by, self.super_user)
        self.assertEqual(
            Panel.objects.get(id=1).modified_by, self.super_user)


@pytest.mark.django_db
class TestGeneAdmin(TestCase):
    def setUp(self):
        self.gene_admin = GeneAdmin(model=Gene, admin_site=AdminSite())
        self.super_user = User.objects.create_superuser(username='super', email='super@email.org',
                                                        password='pass')

        self.gene = mixer.blend('main.Gene', name='Gene_1', added_by=None)

    def test_save_panel_model(self):
        self.gene_admin.save_model(obj=self.gene, request=MockRequest(
            user=self.super_user), form=None, change=None)

        self.assertEqual(
            Gene.objects.get(id=1).added_by, self.super_user)
        self.assertEqual(
            Gene.objects.get(id=1).modified_by, self.super_user)


@pytest.mark.django_db
class TestGeneKeyAdmin(TestCase):
    def setUp(self):
        self.gene_key_admin = GeneKeyAdmin(
            model=GeneKey, admin_site=AdminSite())
        self.super_user = User.objects.create_superuser(username='super', email='super@email.org',
                                                        password='pass')

        self.genekey = mixer.blend(
            'main.GeneKey', key='Gene_key_1', added_by=None)

    def test_save_gene_key_model(self):
        self.gene_key_admin.save_model(obj=self.genekey, request=MockRequest(
            user=self.super_user), form=None, change=None)

        self.assertEqual(
            GeneKey.objects.get(id=1).added_by, self.super_user)
        self.assertEqual(
            GeneKey.objects.get(id=1).modified_by, self.super_user)

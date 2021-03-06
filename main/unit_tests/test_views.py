from django.test import TestCase, Client
from django.contrib.auth.models import User
from mixer.backend.django import mixer
from django.utils import timezone
from django.urls import reverse
import pytest

from main.models import Panel, Gene, Transcript, PanelGene, GeneKey
from main.views import add_key
from main.forms import AddKeyForm
from main.serializers import PanelSerializer, GeneKeySerializer, PanelGeneSerializer

######################
##### Main Views #####
######################

@pytest.mark.django_db
class TestHomeView(TestCase):

    def setUp(self):
        self.client = Client()
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.response = self.client.get(reverse('main-home'))

    def test_home_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_correct_template(self):
        self.assertTemplateUsed(self.response, 'main/home.html')

    def test_home_context(self):
        self.assertEqual(
            self.response.context['panels'].first(), Panel.objects.first())


@pytest.mark.django_db
class TestPanelKeysView(TestCase):

    def setUp(self):
        self.client = Client()
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene = mixer.blend('main.Gene', name='Gene_1')
        self.transcript = mixer.blend(
            'main.Transcript', name='Transcript_1', gene=self.gene)
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene, preferred_transcript=self.transcript)
        self.active_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=True, genes=self.gene)
        self.archived_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_2', checked=True, archived=True, genes=self.gene)

        self.response = self.client.get(
            reverse('panel_keys', kwargs={'pk': 1}))

    def test_panel_keys_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_panel_keys_correct_template(self):
        self.assertTemplateUsed(self.response, 'main/panel_keys.html')

    def test_panel_keys_context(self):
        self.assertEqual(
            self.response.context['panel'].name, 'PANEL_1')

        self.assertEqual(
            self.response.context['active_gene_keys'].first().key, 'GeneKey_1')

        self.assertEqual(
            self.response.context['archived_gene_keys'].first().key, 'GeneKey_2')


@pytest.mark.django_db
class TestAddKeyViewAuthenticated(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.client.login(username='example_user', password='1234')

        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene_on_panel = mixer.blend('main.Gene', name='Gene_1')
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene_on_panel)

        self.url = reverse('add_key', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_add_key_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_add_key_correct_template(self):
        self.assertTemplateUsed(self.response, 'main/add_key.html')

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, AddKeyForm)

    def test_add_key_context(self):
        self.assertEqual(
            self.response.context['panel'].name, 'PANEL_1')

    def test_add_key_POST(self):
        response = self.client.post(self.url, {
            'panel': self.panel.id,
            'key': 'Example_key_1',
            'genes': [self.gene_on_panel.id],
            'comment': 'example comment'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'pending_keys', kwargs={'pk': 1}))
        self.assertEqual(self.panel.gene_keys.first().key, 'Example_key_1')


@pytest.mark.django_db
class TestAddKeyViewUnauthenticated(TestCase):
    def setUp(self):
        self.client = Client()
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.response = self.client.get(reverse('add_key', kwargs={'pk': 1}))

    def test_add_key_status_code(self):
        self.assertEqual(self.response.status_code, 302)

    def test_add_key_check_login_redirect(self):
        assert '/login/' in self.response.url


@pytest.mark.django_db
class TestPendingKeysViewAuthenticated(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.client.login(username='example_user', password='1234')

        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene = mixer.blend('main.Gene', name='Gene_1')
        self.unchecked_genekey = mixer.blend(
            'main.GeneKey', panel=self.panel, key='Example_unchecked_key', checked=False, genes=self.gene)

        self.url = reverse('pending_keys', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_pending_keys_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_pending_keys_correct_template(self):
        self.assertTemplateUsed(self.response, 'main/pending_keys.html')

    def test_pending_keys_context(self):
        self.assertEqual(
            self.response.context['panel'].name, 'PANEL_1')
        self.assertEqual(
            self.response.context['pending_gene_keys'].first().key, 'Example_unchecked_key')


@pytest.mark.django_db
class TestPendingKeysViewUnauthenticated(TestCase):
    def setUp(self):
        self.client = Client()
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.response = self.client.get(
            reverse('pending_keys', kwargs={'pk': 1}))

    def test_add_key_status_code(self):
        self.assertEqual(self.response.status_code, 302)

    def test_add_key_check_login_redirect(self):
        assert '/login/' in self.response.url


@pytest.mark.django_db
class TestGenerateOutputViewAuthenticated(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.client.login(username='example_user', password='1234')

        self.panel = mixer.blend('main.Panel', name='PANEL_1')

        self.url = reverse('generate_output', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_generate_output_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_generate_output_correct_template(self):
        self.assertTemplateUsed(self.response, 'main/generate_output.html')

    def test_generate_output_context(self):
        self.assertEqual(
            self.response.context['panel'].name, 'PANEL_1')
        self.assertEqual(
            self.response.context['panels'].first(), Panel.objects.first())


@pytest.mark.django_db
class TestGenerateOutputViewUnauthenticated(TestCase):
    def setUp(self):
        self.client = Client()
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.response = self.client.get(
            reverse('generate_output', kwargs={'pk': 1}))

    def test_add_key_status_code(self):
        self.assertEqual(self.response.status_code, 302)

    def test_add_key_check_login_redirect(self):
        assert '/login/' in self.response.url


######################
##### AJAX Views #####
######################


@pytest.mark.django_db
class TestLoadGenesView(TestCase):

    def setUp(self):
        self.client = Client()

        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene = mixer.blend('main.Gene', name='Gene_1')
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene)

        self.url = reverse('ajax_load_genes')
        self.response = self.client.get(self.url, {
            'panel': 1
        })

    def test_load_genes_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_load_genes_correct_genes_returned(self):
        self.assertEqual(
            self.response.context['genes'].first().name, 'Gene_1')


######################
##### CRUD Views #####
######################

@pytest.mark.django_db
class TestKeyArchiveView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.client.login(username='example_user', password='1234')

        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene_on_panel = mixer.blend('main.Gene', name='Gene_1')
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene_on_panel)
        self.active_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=True, genes=self.gene_on_panel)
        self.archived_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_2', checked=True, archived=True, genes=self.gene_on_panel)

        self.url = reverse('key_archive', kwargs={'pk': 1, 'key': 1})
        self.response = self.client.get(self.url)

    def test_archive_key_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_archive_key_returns_form(self):
        assert 'html_form' in self.response.json()

    def test_archive_key_POST(self):
        response = self.client.post(
            reverse('key_archive', kwargs={'pk': 1, 'key': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], True)
        self.assertEqual(GeneKey.objects.get(id=1).archived, True)

    def test_archive_already_archived_key_POST(self):
        response = self.client.post(
            reverse('key_archive', kwargs={'pk': 1, 'key': 2}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], False)


@pytest.mark.django_db
class TestKeyCommentView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.client.login(username='example_user', password='1234')

        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene_on_panel = mixer.blend('main.Gene', name='Gene_1')
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene_on_panel)
        self.active_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=True, genes=self.gene_on_panel, comment='example_comment', modified_at=timezone.now())
        self.archived_gene_key = mixer.blend('main.GeneKey', panel=self.panel, key='GeneKey_2', checked=True,
                                             archived=True, genes=self.gene_on_panel, comment='example_comment', modified_at=timezone.now())

        self.url = reverse('key_comment', kwargs={'pk': 1, 'key': 1})
        self.response = self.client.get(self.url)

    def test_key_comment_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_key_comment_returns_form(self):
        assert 'html_form' in self.response.json()

    def test_key_comment_POST(self):
        stored_time = GeneKey.objects.get(
            id=1).modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f")

        response = self.client.post(
            reverse('key_comment', kwargs={'pk': 1, 'key': 1}), {
                'comment': 'updated_comment',
                'stored_time': stored_time
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], True)
        self.assertEqual(GeneKey.objects.get(id=1).comment, 'updated_comment')

    def test_archived_key_comment_POST(self):
        stored_time = GeneKey.objects.get(
            id=2).modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f")

        response = self.client.post(
            reverse('key_comment', kwargs={'pk': 1, 'key': 2}), {
                'comment': 'updated_comment',
                'stored_time': stored_time
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], False)
        self.assertEqual(GeneKey.objects.get(id=2).comment, 'example_comment')

    def test_key_comment_already_updated_POST(self):
        stored_time = GeneKey.objects.get(
            id=1).modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f")

        key = GeneKey.objects.get(id=1)
        key.comment = 'manual_update'
        key.save()

        response = self.client.post(
            reverse('key_comment', kwargs={'pk': 1, 'key': 1}), {
                'comment': 'updated_comment',
                'stored_time': stored_time
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], False)
        self.assertEqual(GeneKey.objects.get(id=1).comment, 'manual_update')

@pytest.mark.django_db
class TestPanelGeneEditView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.client.login(username='example_user', password='1234')

        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene_on_panel = mixer.blend('main.Gene', name='Gene_1')
        self.transcript1 = mixer.blend('main.Transcript', name='Transcript_1', gene=self.gene_on_panel)
        self.transcript2 = mixer.blend('main.Transcript', name='Transcript_2', gene=self.gene_on_panel)
        self.transcript3 = mixer.blend('main.Transcript', name='Transcript_3', gene=self.gene_on_panel)
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene_on_panel, preferred_transcript=self.transcript1, modified_at=timezone.now())

        self.url = reverse('panel_gene_edit', kwargs={'pk': 1, 'panel_gene': 1})
        self.response = self.client.get(self.url)

    def test_panel_gene_edit_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_panel_gene_edit_returns_form(self):
        assert 'html_form' in self.response.json()

    def test_panel_gene_edit_POST(self):
        stored_time = PanelGene.objects.get(
            id=1).modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f")

        response = self.client.post(
            reverse('panel_gene_edit', kwargs={'pk': 1, 'panel_gene': 1}), {
                'preferred_transcript': self.transcript2.id,
                'stored_time': stored_time
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], True)
        self.assertEqual(PanelGene.objects.get(id=1).preferred_transcript.name, 'Transcript_2')

    def test_panel_gene_edit_already_updated_POST(self):
        stored_time = PanelGene.objects.get(
            id=1).modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f")

        panelgene = PanelGene.objects.get(id=1)
        panelgene.preferred_transcript = self.transcript3
        panelgene.save()

        response = self.client.post(
            reverse('panel_gene_edit', kwargs={'pk': 1, 'panel_gene': 1}), {
                'preferred_transcript': self.transcript2.id,
                'stored_time': stored_time
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], False)
        self.assertEqual(PanelGene.objects.get(id=1).preferred_transcript.name, 'Transcript_3')


@pytest.mark.django_db
class TestKeyAcceptView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.client.login(username='example_user', password='1234')

        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene_on_panel = mixer.blend('main.Gene', name='Gene_1')
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene_on_panel)
        self.inactive_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=False, genes=self.gene_on_panel)
        self.active_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_2', checked=True, genes=self.gene_on_panel)

        self.url = reverse('key_accept', kwargs={'pk': 1, 'key': 1})
        self.response = self.client.get(self.url)

    def test_accept_key_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_accept_key_returns_form(self):
        assert 'html_form' in self.response.json()

    def test_accept_key_POST(self):
        response = self.client.post(
            reverse('key_accept', kwargs={'pk': 1, 'key': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], True)
        self.assertEqual(GeneKey.objects.get(id=1).checked, True)

    def test_accept_already_accepted_key_POST(self):
        response = self.client.post(
            reverse('key_accept', kwargs={'pk': 1, 'key': 2}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], False)

    def test_accept_deleted_key_POST(self):
        response = self.client.post(
            reverse('key_accept', kwargs={'pk': 1, 'key': 4}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], False)


@pytest.mark.django_db
class TestKeyDeleteView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.client.login(username='example_user', password='1234')

        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene_on_panel = mixer.blend('main.Gene', name='Gene_1')
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene_on_panel)
        self.inactive_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=False, genes=self.gene_on_panel)
        self.active_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_2', checked=True, genes=self.gene_on_panel)

        self.url = reverse('key_delete', kwargs={'pk': 1, 'key': 1})
        self.response = self.client.get(self.url)

    def test_delete_key_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_delete_key_returns_form(self):
        assert 'html_form' in self.response.json()

    def test_delete_key_POST(self):
        response = self.client.post(
            reverse('key_delete', kwargs={'pk': 1, 'key': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], True)
        self.assertFalse(GeneKey.objects.filter(id=1).exists())

    def test_delete_accepted_key_POST(self):
        response = self.client.post(
            reverse('key_delete', kwargs={'pk': 1, 'key': 2}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], False)

    def test_delete_already_deleted_key_POST(self):
        response = self.client.post(
            reverse('key_delete', kwargs={'pk': 1, 'key': 4}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['form_is_valid'], False)

#############################
##### Output Generation #####
#############################


@pytest.mark.django_db
class TestOutputGenerationView(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='example_user', password='1234')
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene = mixer.blend('main.Gene', name='Gene_1')
        self.transcript = mixer.blend('main.Transcript', name='Transcript_1')
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene, preferred_transcript=self.transcript)
        self.gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=True, genes=self.gene,
            added_by=self.user, added_at=timezone.now(), checked_by=self.user, checked_at=timezone.now())

        self.url = reverse('generate_excel', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_output_generation_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_output_generation_returns_excel(self):
        self.assertEqual(self.response['content-type'], 'application/ms-excel')


###############
##### API #####
###############

@pytest.mark.django_db
class TestPanelAPIView(TestCase):

    def setUp(self):
        self.client = Client()
        self.panel_1 = mixer.blend('main.Panel', name='PANEL_1')
        self.panel_2 = mixer.blend('main.Panel', name='Panel_2')
        self.panel_3 = mixer.blend('main.Panel', name='Panel_3')
        self.panel_4 = mixer.blend('main.Panel', name='Panel_4')
        self.panel_5 = mixer.blend('main.Panel', name='Panel_5')

    def test_panel_return_all(self):
        response = self.client.get('/api/', {'panel': ''})
        panels = Panel.objects.all()
        serializer = PanelSerializer(panels, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, 200)

    def test_panel_valid_query(self):
        response = self.client.get('/api/', {'panel': 2})
        panels = Panel.objects.filter(id=2)
        serializer = PanelSerializer(panels, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, 200)


@pytest.mark.django_db
class TestGeneKeyAPIView(TestCase):

    def setUp(self):
        self.client = Client()
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.gene_key1 = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=True, genes=mixer.RANDOM)
        self.gene_key2 = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_2', checked=True, genes=mixer.RANDOM)
        self.gene_key3 = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_3', checked=True, genes=mixer.RANDOM)
        self.gene_key3 = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_4', checked=True, genes=mixer.RANDOM)

    def test_active_gene_key_valid_numerical_query(self):
        response = self.client.get('/api/1/active_keys')
        active_gene_keys = GeneKey.objects.filter(
            panel=1).exclude(archived=True).exclude(checked=False).order_by('-added_at')
        serializer = GeneKeySerializer(active_gene_keys, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, 200)

    def test_active_gene_key_valid_text_query(self):
        response = self.client.get('/api/Panel_1/active_keys')
        active_gene_keys = GeneKey.objects.filter(
            panel=1).exclude(archived=True).exclude(checked=False).order_by('-added_at')
        serializer = GeneKeySerializer(active_gene_keys, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, 200)


@pytest.mark.django_db
class TestPanelGeneAPIView(TestCase):

    def setUp(self):
        self.client = Client()
        self.panel = mixer.blend('main.Panel', name='PANEL_1')
        self.panel_gene1 = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=mixer.RANDOM, preferred_transcript=mixer.RANDOM)
        self.panel_gene2 = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=mixer.RANDOM, preferred_transcript=mixer.RANDOM)
        self.panel_gene3 = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=mixer.RANDOM, preferred_transcript=mixer.RANDOM)
        self.panel_gene4 = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=mixer.RANDOM, preferred_transcript=mixer.RANDOM)

    def test_active_gene_key_valid_numerical_query(self):
        response = self.client.get('/api/1/genes')
        panel_genes = PanelGene.objects.filter(panel=1).order_by('gene__name')
        serializer = PanelGeneSerializer(panel_genes, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, 200)

    def test_active_gene_key_valid_text_query(self):
        response = self.client.get('/api/panel_1/genes')
        panel_genes = PanelGene.objects.filter(panel=1).order_by('gene__name')
        serializer = PanelGeneSerializer(panel_genes, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, 200)

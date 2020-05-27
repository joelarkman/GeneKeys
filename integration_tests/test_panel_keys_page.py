from selenium import webdriver
from main.models import Panel, GeneKey, PanelGene
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from mixer.backend.django import mixer
import time


class TestPanelKeysPage_placeholders(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('integration_tests/chromedriver')
        self.panel = mixer.blend('main.Panel', name='PANEL_1', id=1)

    def tearDown(self):
        self.browser.close()

    def test_active_keys_placeholder_is_displayed(self):
        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        # Test table placeholder for no active keys
        placeholder = self.browser.find_element_by_id(
            'active-keys-table').find_element_by_class_name('dataTables_empty').text

        self.assertEqual(placeholder,
                         'No active keys for the PANEL_1 panel')

    def test_archived_keys_placeholder_is_displayed(self):
        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        self.browser.find_element_by_link_text(
            'Archived keys').click()

        # Test table placeholder for no archived keys
        placeholder = self.browser.find_element_by_id(
            'archived-keys-table').find_element_by_class_name('dataTables_empty').text

        self.assertEqual(placeholder,
                         'No archived keys for the PANEL_1 panel')

    def test_gene_transcript_list_placeholder_is_displayed(self):
        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        self.browser.find_element_by_link_text(
            'Gene/transcript list').click()

        # Test table placeholder for no archived keys
        placeholder = self.browser.find_element_by_id(
            'panel-genes-table').find_element_by_class_name('dataTables_empty').text

        self.assertEqual(placeholder,
                         'No genes associated with the PANEL_1 panel')


class TestPanelKeysPage(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('integration_tests/chromedriver')
        self.panel = mixer.blend('main.Panel', name='PANEL_1', id=1)
        self.gene = mixer.blend('main.Gene', name='Gene_1')
        self.transcript = mixer.blend(
            'main.Transcript', name='Transcript_1', gene=self.gene)
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene, preferred_transcript=self.transcript)
        self.active_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=True, genes=self.gene, id=1)
        self.archived_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_2', checked=True, archived=True, genes=self.gene, id=2)

        self.user = User.objects.create_user(
            username='example_user', password='1234')

        self.browser.get(self.live_server_url + '/login/')
        username_input = self.browser.find_element_by_name("username")
        username_input.send_keys('example_user')
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys('1234')
        self.browser.find_element_by_xpath(
            '/html/body/div/div/div[2]/form/input[2]').click()

    def tearDown(self):
        self.browser.close()

    def test_panel_key_active_gene_key_is_listed(self):

        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        # Test table placeholder for no active keys
        key = self.browser.find_element_by_xpath(
            '//*[@id="active-keys-table"]/tbody/tr[1]/td[1]').text

        self.assertEqual(key,
                         'GeneKey_1')

    def test_panel_key_archived_gene_key_is_listed(self):

        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        self.browser.find_element_by_link_text(
            'Archived keys').click()

        # Test table placeholder for no active keys
        key = self.browser.find_element_by_xpath(
            '//*[@id="archived-keys-table"]/tbody/tr[1]/td[1]').text

        self.assertEqual(key,
                         'GeneKey_2')

    def test_panel_key_view_comment(self):

        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        # Test clicking view comment
        self.browser.find_element_by_xpath(
            '//*[@id="active-keys-table"]/tbody/tr[1]/td[7]/div/button[2]').click()

        time.sleep(1)

        comment_title = self.browser.find_element_by_xpath(
            '//*[@id="modal-keys"]/div[1]').text

        self.assertEqual(comment_title,
                         'Comment for GeneKey_1')

    def test_panel_key_archive_comment(self):

        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        # Test clicking view comment
        self.browser.find_element_by_xpath(
            '//*[@id="active-keys-table"]/tbody/tr[1]/td[7]/div/button[1]').click()

        time.sleep(1)

        archive_title = self.browser.find_element_by_xpath(
            '//*[@id="modal-keys"]/div[1]').text

        self.assertEqual(archive_title,
                         'Archive Gene Key')

    def test_panel_key_set_preferred_transcript(self):

        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        self.browser.find_element_by_link_text(
            'Gene/transcript list').click()

        # Test clicking view comment
        self.browser.find_element_by_xpath(
            '//*[@id="panel-genes-table"]/tbody/tr[1]/td[4]/button').click()

        time.sleep(1)

        set_preferred_transcript_title = self.browser.find_element_by_xpath(
            '//*[@id="modal-keys"]/div[1]').text

        self.assertEqual(set_preferred_transcript_title,
                         'Set preferred transcript')

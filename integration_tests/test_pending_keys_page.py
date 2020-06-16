from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from main.models import Panel, GeneKey, PanelGene
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from mixer.backend.django import mixer
import time


class TestPendingKeysPage_placeholder(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('integration_tests/chromedriver')
        self.panel = mixer.blend('main.Panel', name='PANEL_1', id=1)

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

    def test_pending_keys_placeholder_is_displayed(self):
        self.browser.get(self.live_server_url +
                         reverse('pending_keys', kwargs={'pk': 1}))

        # Test table placeholder for no active keys
        placeholder = self.browser.find_element_by_id(
            'pending-keys-table').find_element_by_class_name('dataTables_empty').text

        self.assertEqual(placeholder,
                         'No keys pending approval')


class TestPendingKeysPage(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('integration_tests/chromedriver')
        self.panel = mixer.blend('main.Panel', name='PANEL_1', id=1)
        self.gene = mixer.blend('main.Gene', name='Gene_1')
        self.transcript = mixer.blend(
            'main.Transcript', name='Transcript_1', gene=self.gene)
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene, preferred_transcript=self.transcript)
        self.pending_gene_key = mixer.blend(
            'main.GeneKey', panel=self.panel, key='GeneKey_1', checked=False, genes=self.gene, id=1)

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

    def test_pending_gene_key_is_listed(self):

        self.browser.get(self.live_server_url +
                         reverse('pending_keys', kwargs={'pk': 1}))

        # Test table placeholder for no active keys
        key = self.browser.find_element_by_xpath(
            '//*[@id="pending-keys-table"]/tbody/tr[1]/td[1]').text

        self.assertEqual(key,
                         'GeneKey_1')

    def test_view_accept_key(self):

        self.browser.get(self.live_server_url +
                         reverse('pending_keys', kwargs={'pk': 1}))

        # Test clicking view comment
        self.browser.find_element_by_xpath(
            '//*[@id="pending-keys-table"]/tbody/tr[1]/td[7]/div/div[2]/button').click()

        time.sleep(1)

        accept_key_title = self.browser.find_element_by_xpath(
            '//*[@id="modal-keys"]/div[1]').text

        self.assertEqual(accept_key_title,
                         'Accept Gene Key')

    def test_view_delete_key(self):

        self.browser.get(self.live_server_url +
                         reverse('pending_keys', kwargs={'pk': 1}))

        # Test clicking view comment
        self.browser.find_element_by_xpath(
            '//*[@id="pending-keys-table"]/tbody/tr[1]/td[7]/div/div[1]/button').click()

        time.sleep(1)

        delete_key_title = self.browser.find_element_by_xpath(
            '//*[@id="modal-keys"]/div[1]').text

        self.assertEqual(delete_key_title,
                         'Delete Gene Key')

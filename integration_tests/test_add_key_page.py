from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from main.models import Panel, GeneKey, PanelGene
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from mixer.backend.django import mixer
import time


class TestAddKeyPage(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('integration_tests/chromedriver')
        self.panel = mixer.blend('main.Panel', name='PANEL_1', id=1)
        self.gene = mixer.blend('main.Gene', name='Gene_1')
        self.transcript = mixer.blend(
            'main.Transcript', name='Transcript_1', gene=self.gene)
        self.panel_gene = mixer.blend(
            'main.PanelGene', panel=self.panel, gene=self.gene, preferred_transcript=self.transcript)

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

    def test_add_key_form(self):

        self.browser.get(self.live_server_url +
                         reverse('panel_keys', kwargs={'pk': 1}))

        self.browser.find_element_by_link_text(
            'Add key').click()

        key_input = self.browser.find_element_by_name("key")
        key_input.send_keys('example_key_addition')

        self.browser.find_element_by_xpath(
            '//*[@id="genekeyForm"]/div[3]/div').click()

        self.browser.find_element_by_xpath(
            '//*[@id="genekeyForm"]/div[3]/div').send_keys(Keys.ENTER)

        comment_input = self.browser.find_element_by_name("comment")
        comment_input.send_keys('example_comment')

        self.browser.find_element_by_xpath(
            '//*[@id="genekeyForm"]/button').click()

        self.assertTrue(isinstance(GeneKey.objects.get(
            key='example_key_addition'), GeneKey))

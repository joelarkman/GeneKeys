from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from main.models import Panel, GeneKey, PanelGene
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from mixer.backend.django import mixer
import time


class TestGenerateOutputPage(StaticLiveServerTestCase):

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

    def test_panels_are_displayed(self):
        self.browser.get(self.live_server_url +
                         reverse('generate_output', kwargs={'pk': 1}))

        # The user sees panel is on screen.
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/div[3]/div[3]/div[2]/div[1]/a').find_element_by_tag_name('h2').text,
                         'PANEL_1')

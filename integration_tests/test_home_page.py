from selenium import webdriver
from main.models import Panel
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from mixer.backend.django import mixer
import time


class TestHomePage_no_panel(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('integration_tests/chromedriver')

    def tearDown(self):
        self.browser.close()

    def test_no_panels_alert_is_displayed(self):
        self.browser.get(self.live_server_url)

        # The user requests page before panels have been added.
        alert = self.browser.find_element_by_xpath('/html/body/div[4]/div')
        self.assertEqual(alert.find_element_by_tag_name('p').text,
                         'No panels added yet. Plase navigate to the admin site and consult with the standard operating procedure to get started.')


class TestHomePage_with_panel(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('integration_tests/chromedriver')
        self.panel = mixer.blend('main.Panel', name='PANEL_1', id=1)

    def tearDown(self):
        self.browser.close()

    def test_panels_are_displayed(self):
        self.browser.get(self.live_server_url)

        # The user sees panel is on screen.
        self.assertEqual(self.browser.find_element_by_class_name('ui.fluid.link.card').find_element_by_tag_name('h1').text,
                         'PANEL_1')

    def test_panels_link_functions(self):
        self.browser.get(self.live_server_url)

        # Test redirect to panel keys page.
        panel_keys_url = self.live_server_url + \
            reverse('panel_keys', kwargs={'pk': 1})
        self.browser.find_element_by_class_name('ui.fluid.link.card').click()
        self.assertEqual(self.browser.current_url,
                         panel_keys_url)

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from main.views import home, panel_keys, add_key, pending_keys, generate_output


class TestUrls(SimpleTestCase):

    def test_home_url_resolves(self):
        url = reverse('main-home')
        self.assertEqual(resolve(url).func, home)

    def test_panel_keys_url_resolves(self):
        url = reverse('panel_keys', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func, panel_keys)

    def test_add_key_url_resolves(self):
        url = reverse('add_key', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func, add_key)

    def test_pending_keys_url_resolves(self):
        url = reverse('pending_keys', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func, pending_keys)

    def test_generate_output_url_resolves(self):
        url = reverse('generate_output', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func, generate_output)

from django.test import TestCase
from django.urls import reverse


# Create your tests here.

class MaturaHomepageTests(TestCase):
    def test_home_page_status_code(self):
        response = self.client.get('/matura/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rodzaje zadań")

    def test_view_url_by_name(self):
        response = self.client.get(reverse('matura_home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('matura_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'matura/matura_home.html')

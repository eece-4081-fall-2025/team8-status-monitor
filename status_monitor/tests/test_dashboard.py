from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='homeusertest',
            password='HomePass123!'
        )
        self.client.login(username=self.user.username, password='HomePass123!')
        self.home_url = reverse('home')
        
    def test_home_page_loads_successfully(self):
        response=self.client.get(self.home_url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response, "Welcome to the status monitor")

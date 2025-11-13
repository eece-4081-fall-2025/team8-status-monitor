from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from status_monitor.models import MonitoredSite


class SiteManagementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="SecurePass123!"
        )
        self.client.login(username=self.user.username, password="SecurePass123!")

        self.list_url = reverse("site_list")
        self.create_url = reverse("site_create")

        self.site = MonitoredSite.objects.create(
            user=self.user,
            name="Test Site",
            url="https://example.com",
            check_frequency=5,
        )

        self.edit_url = reverse("site_edit", args=[self.site.pk])
        self.delete_url = reverse("site_delete", args=[self.site.pk])

    def test_site_list_loads(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("test site".lower(), response.content.decode().lower())

    def test_can_create_new_site(self):
        data = {
            "name": "New Site",
            "url": "https://newsite.com",
            "check_frequency": 5,
        }
        response = self.client.post(self.create_url, data, follow=True)
        self.assertEqual(MonitoredSite.objects.filter(user=self.user).count(), 2)
        self.assertIn("new site".lower(), response.content.decode().lower())

    def test_can_edit_existing_site(self):
        data = {
            "name": "Updated Site",
            "url": "https://updatedsite.com",
            "check_frequency": 10,
        }
        response = self.client.post(self.edit_url, data, follow=True)
        self.site.refresh_from_db()
        self.assertEqual(self.site.name, "Updated Site".title())
        self.assertEqual(self.site.url, "https://updatedsite.com")
        self.assertIn("updated site".lower(), response.content.decode().lower())

    def test_can_delete_site(self):
        response = self.client.post(self.delete_url, follow=True)
        self.assertEqual(MonitoredSite.objects.filter(user=self.user).count(), 0)
        content = response.content.decode().lower()
        self.assertTrue(
            "no site" in content or "no sites yet" in content or "no monitored sites" in content
        )

    def test_unauthenticated_redirect(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

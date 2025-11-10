# status_monitor/tests/test_dashboard.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from status_monitor.models import MonitoredSite, SiteCheckResult


# ---------------------------------------------------------------------
# HOME VIEW TESTS
# ---------------------------------------------------------------------
class HomeViewTest(TestCase):
    """Verify home redirects properly to the status dashboard."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="homeusertest",
            password="HomePass123!",
        )
        self.home_url = reverse("home")
        self.status_url = reverse("status_page")

    def test_home_redirects_to_status_page(self):
        """Home view should redirect to /status/."""
        self.client.login(username="homeusertest", password="HomePass123!")
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.status_url)

    def test_home_requires_login(self):
        """Anonymous users should be redirected to login."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


# ---------------------------------------------------------------------
# STATUS PAGE TESTS
# ---------------------------------------------------------------------
class StatusPageTest(TestCase):
    """Test the functionality and data rendering of the Status Dashboard."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="statususer", password="StatusPass123!"
        )
        self.client.login(username="statususer", password="StatusPass123!")
        self.status_url = reverse("status_page")

        # Create monitored sites
        self.site1 = MonitoredSite.objects.create(
            user=self.user,
            name="Test Site 1", url="https://example1.com"
        )
        self.site2 = MonitoredSite.objects.create(
            user=self.user,
            name="Test Site 2", url="https://example2.com"
        )

        # Add history checks
        now = timezone.now()
        SiteCheckResult.objects.create(
            site=self.site1,
            timestamp=now - timedelta(minutes=5),
            is_up=True,
            response_time=0.5,
            status_code=200,
        )
        SiteCheckResult.objects.create(
            site=self.site2,
            timestamp=now - timedelta(minutes=3),
            is_up=False,
            response_time=1.2,
            status_code=500,
        )

    def test_status_page_loads(self):
        """Dashboard should load successfully."""
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status Dashboard")

    def test_status_page_displays_sites(self):
        """All monitored sites should appear in rendered HTML."""
        response = self.client.get(self.status_url)
        self.assertContains(response, "https://example1.com")
        self.assertContains(response, "https://example2.com")

    def test_status_page_displays_site_status(self):
        """Each site should show its current status (Up / Down)."""
        response = self.client.get(self.status_url)
        html = response.content.decode().lower()
        self.assertIn("up", html)
        self.assertIn("down", html)

    def test_status_page_displays_response_time(self):
        """Response times should appear in HTML."""
        response = self.client.get(self.status_url)
        self.assertContains(response, "0.5")
        self.assertContains(response, "1.2")

    def test_status_page_context_contains_site_data(self):
        """The view context should include site_data."""
        response = self.client.get(self.status_url)
        self.assertIn("site_data", response.context)
        site_data = response.context["site_data"]
        self.assertTrue(any(d["site"].url == "https://example1.com" for d in site_data))
        self.assertTrue(any(d["site"].url == "https://example2.com" for d in site_data))

    def test_status_page_requires_login(self):
        """Anonymous users should be redirected."""
        self.client.logout()
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_site_ordering(self):
        """Ensure sites appear sorted alphabetically by URL in context."""
        response = self.client.get(self.status_url)
        site_data = response.context["site_data"]
        urls = [d["site"].url for d in site_data]
        self.assertEqual(urls, sorted(urls))

    def test_site_with_no_checks_shows_never(self):
        """Sites without history should display 'Never' as last check."""
        site3 = MonitoredSite.objects.create(user=self.user,name="Empty Site", url="https://example3.com")
        response = self.client.get(self.status_url)
        html = response.content.decode()
        self.assertIn("Never", html)


# ---------------------------------------------------------------------
# MAINTENANCE PAGE TESTS
# ---------------------------------------------------------------------
class MaintenancePageTest(TestCase):
    """Ensure maintenance page is accessible."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="maintuser", password="MaintPass123!"
        )
        self.client.login(username='maintuser', password='MaintPass123!')
        self.maintenance_url = reverse("maintenance_page")

    def test_maintenance_page_loads(self):
        response = self.client.get(self.maintenance_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maintenance")


# ---------------------------------------------------------------------
# INCIDENTS PAGE TESTS
# ---------------------------------------------------------------------
class IncidentsPageTest(TestCase):
    """Ensure incident page loads properly."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="incidentuser", password="IncidentPass123!"
        )
        self.client.login( username="incidentuser", password="IncidentPass123!")
        self.incidents_url = reverse("incidents_page")

    def test_incidents_page_loads(self):
        response = self.client.get(self.incidents_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incident")
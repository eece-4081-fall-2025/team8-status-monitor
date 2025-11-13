from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from status_monitor.models import MonitoredSite, SiteCheckResult
from django.utils import timezone


# -----------------------------
# Registration Tests
# -----------------------------
class UserRegistrationTests(TestCase):
    """Test user registration functionality."""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")

    def test_registration_page_loads(self):
        """Registration page renders correctly."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")

    def test_successful_registration_creates_user(self):
        """Valid registration creates user and redirects."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        response = self.client.post(self.register_url, data, follow=True)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, "testuser")

        # Depending on your view, user may or may not be logged in automatically
        self.assertIn(response.status_code, [200, 302])

    def test_registration_password_mismatch(self):
        """Registration fails when passwords do not match."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "SecurePass123!",
            "password2": "DifferentPass!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 0)
        self.assertContains(response, "password")

    def test_registration_duplicate_username(self):
        """Duplicate username should be rejected."""
        User.objects.create_user("testuser", "test@example.com", "pass123")
        data = {
            "username": "testuser",
            "email": "another@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        response = self.client.post(self.register_url, data)
        self.assertContains(response, "username")

    def test_redirect_if_already_authenticated(self):
        """Authenticated user visiting registration should redirect."""
        user = User.objects.create_user("existing", password="pass123")
        self.client.login(username="existing", password="pass123")
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("status_page"))


# -----------------------------
# Login / Logout Tests
# -----------------------------
class UserLoginLogoutTests(TestCase):
    """Test user login and logout behavior."""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
        )

    def test_login_page_loads(self):
        """Login page loads successfully."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")

    def test_successful_login_redirects_to_status_page(self):
        """Valid login redirects to status dashboard."""
        response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "SecurePass123!"},
            follow=True,
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Status")

    def test_login_invalid_credentials(self):
        """Invalid login credentials should fail."""
        response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "WrongPass!"},
        )
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid")


    def test_authenticated_user_redirected_from_login(self):
        """Logged-in user visiting login should redirect to dashboard."""
        self.client.login(username="testuser", password="SecurePass123!")
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("status_page"))

    def test_logout_redirects_to_login(self):
        """Logging out should clear session and redirect."""
        self.client.login(username="testuser", password="SecurePass123!")
        response = self.client.post(self.logout_url, follow=True)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Login")


# -----------------------------
# Protected View Access
# -----------------------------
class ProtectedViewTests(TestCase):
    """Test login protection on restricted pages."""

    def setUp(self):
        self.client = Client()
        self.status_url = reverse("status_page")
        self.home_url = self.status_url
        self.login_url = reverse("login")
        self.user = User.objects.create_user(
            username="protecteduser",
            password="SecurePass123!",
        )

    def test_home_accessible_when_logged_in(self):
        """Test home (status dashboard) is accessible when logged in"""
        logged_in = self.client.login(username='protecteduser', password='SecurePass123!')
        self.assertTrue(logged_in, "Login failed — check credentials.")
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Status Monitor')

    def test_home_requires_login(self):
        """Test home redirects to login when not authenticated"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_redirect_when_not_authenticated(self):
        """Anonymous user should be redirected to login."""
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        self.assertIn('next=', response.url)

    def test_protected_view_preserves_next_parameter(self):
        """Test redirect to login preserves original URL"""
        response = self.client.get(self.home_url)
        self.assertIn(f'next={self.home_url}', response.url)
        self.assertIn("/login/", response.url)
        self.assertIn("next=", response.url)

    def test_access_when_logged_in(self):
        """Authenticated user can access status dashboard."""
        self.client.login(username="protecteduser", password="SecurePass123!")
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status")
    
    def test_status_page_displays_user_sites(self):
        """Dashboard displays monitored sites and uptime data."""
        site = MonitoredSite.objects.create(
            name="Example Site",
            url="https://example.com",
            user=self.user,
        )
        SiteCheckResult.objects.create(
            site=site,
            timestamp=timezone.now(),
            is_up=True,
            response_time=0.15,
        )

        self.client.login(username="protecteduser", password="SecurePass123!")
        response = self.client.get(reverse("status_page"))
        self.assertContains(response, "Example Site")
        self.assertIn("site_data", response.context)

    

# -----------------------------
# Session Tests
# -----------------------------
class UserSessionTests(TestCase):
    """Test login session persistence and cleanup."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sessionuser",
            password="SecurePass123!",
        )

    def test_session_persists_after_login(self):
        """User session remains authenticated across requests."""
        self.client.login(username="sessionuser", password="SecurePass123!")
        first = self.client.get(reverse("status_page"))
        second = self.client.get(reverse("status_page"))
        self.assertTrue(first.wsgi_request.user.is_authenticated)
        self.assertTrue(second.wsgi_request.user.is_authenticated)

    def test_session_cleared_after_logout(self):
        """User session clears properly after logout."""
        self.client.login(username="sessionuser", password="SecurePass123!")
        self.client.post(reverse("logout"))
        response = self.client.get(reverse("status_page"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

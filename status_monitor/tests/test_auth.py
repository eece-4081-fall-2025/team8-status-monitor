from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class UserRegistrationTests(TestCase):
    """Test user registration functionality"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_registration_page_loads(self):
        """Test that registration page is accessible"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')
    
    def test_successful_registration(self):
        """Test user can register with valid data"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
        # User should be auto-logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_registration_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 0)
        self.assertContains(response, "password")
    
    def test_registration_duplicate_username(self):
        """Test registration fails with duplicate username"""
        User.objects.create_user('testuser', 'test@example.com', 'pass123')
        data = {
            'username': 'testuser',
            'email': 'another@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, 'username')
    
    def test_registration_weak_password(self):
        """Test registration fails with weak password"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': '123',
            'password2': '123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 0)
        self.assertContains(response, 'password')
    
    def test_registration_empty_username(self):
        """Test registration fails with empty username"""
        data = {
            'username': '',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 0)
    
    def test_registration_redirects_when_authenticated(self):
        """Test logged-in users are redirected from registration"""
        user = User.objects.create_user('existing', password='pass123')
        self.client.login(username='existing', password='pass123')
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))


class UserLoginTests(TestCase):
    """Test user login functionality"""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
    
    def test_login_page_loads(self):
        """Test that login page is accessible"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_successful_login(self):
        """Test user can login with valid credentials"""
        data = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.login_url, data, follow=True)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'testuser')
    
    def test_login_invalid_username(self):
        """Test login fails with invalid username"""
        data = {
            'username': 'wronguser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'Invalid')
    
    def test_login_invalid_password(self):
        """Test login fails with invalid password"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'Invalid')
    
    def test_login_empty_fields(self):
        """Test login fails with empty credentials"""
        data = {
            'username': '',
            'password': ''
        }
        response = self.client.post(self.login_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_redirects_to_next(self):
        """Test login redirects to 'next' parameter"""
        data = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(
            f"{self.login_url}?next=/dashboard/",
            data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/')
    
    def test_login_redirects_when_authenticated(self):
        """Test authenticated users redirected from login page"""
        self.client.login(username='testuser', password='SecurePass123!')
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))


class UserLogoutTests(TestCase):
    """Test user logout functionality"""
    
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!'
        )
        self.client.login(username='testuser', password='SecurePass123!')
    
    def test_logout_confirmation_page(self):
        """Test GET request shows confirmation page"""
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'logout')
    
    def test_logout_functionality(self):
        """Test user can successfully logout"""
        # Verify user is logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        response = self.client.post(self.logout_url)
        
        # Verify user is logged out
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_redirects(self):
        """Test logout redirects to login page"""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
    
    def test_logout_shows_message(self):
        """Test logout displays success message"""
        response = self.client.post(self.logout_url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any('logged out' in str(m).lower() for m in messages))


class ProtectedViewTests(TestCase):
    """Test that views are protected by login requirement"""
    
    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('dashboard')
        self.user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!'
        )
    
    def test_dashboard_requires_login(self):
        """Test dashboard redirects to login when not authenticated"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        self.assertIn('next=', response.url)
    
    def test_dashboard_accessible_when_logged_in(self):
        """Test dashboard is accessible when logged in"""
        self.client.login(username='testuser', password='SecurePass123!')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_protected_view_preserves_next_parameter(self):
        """Test redirect to login preserves original URL"""
        response = self.client.get(self.dashboard_url)
        self.assertIn(f'next={self.dashboard_url}', response.url)


class UserSessionTests(TestCase):
    """Test user session management"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!'
        )
    
    def test_session_persists_across_requests(self):
        """Test user session persists after login"""
        self.client.login(username='testuser', password='SecurePass123!')
        
        # First request
        response1 = self.client.get(reverse('dashboard'))
        self.assertTrue(response1.wsgi_request.user.is_authenticated)
        
        # Second request
        response2 = self.client.get(reverse('dashboard'))
        self.assertTrue(response2.wsgi_request.user.is_authenticated)
        self.assertEqual(
            response1.wsgi_request.user.id,
            response2.wsgi_request.user.id
        )
    
    def test_session_cleared_after_logout(self):
        """Test session is cleared after logout"""
        self.client.login(username='testuser', password='SecurePass123!')
        
        # Verify session exists
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        self.client.post(reverse('logout'))
        
        # Verify session cleared
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_anonymous_user_has_no_session(self):
        """Test unauthenticated user has no auth session"""
        response = self.client.get(reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, '')


class CSRFProtectionTests(TestCase):
    """Test CSRF protection on authentication forms"""
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!'
        )
    
    def test_login_requires_csrf_token(self):
        """Test login POST requires CSRF token"""
        data = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        # This should fail without CSRF token
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 403)
    
    def test_registration_requires_csrf_token(self):
        """Test registration POST requires CSRF token"""
        data = {
            'username': 'newuser',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 403)


class AuthenticationEdgeCasesTests(TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.client = Client()
    
    def test_login_with_inactive_user(self):
        """Test inactive users cannot login"""
        user = User.objects.create_user(
            username='inactive',
            password='pass123'
        )
        user.is_active = False
        user.save()
        
        data = {
            'username': 'inactive',
            'password': 'pass123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_case_sensitive_username(self):
        """Test username is case-sensitive"""
        User.objects.create_user('TestUser', password='pass123')
        
        # Try logging in with different case
        data = {
            'username': 'testuser',  # lowercase
            'password': 'pass123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_whitespace_in_credentials(self):
        """Test handling of whitespace in credentials"""
        User.objects.create_user('testuser', password='pass123')
        
        data = {
            'username': ' testuser ',  # with spaces
            'password': 'pass123'
        }
        response = self.client.post(reverse('login'), data)
        # Should fail - whitespace not trimmed
        self.assertFalse(response.wsgi_request.user.is_authenticated)
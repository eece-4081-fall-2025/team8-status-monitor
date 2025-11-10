from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
# --- REQUIRED IMPORTS FOR EPIC 1 ---
from status_monitor.models import Site, UserProfile 
from django.contrib.messages import get_messages 
# ------------------------------------


# --- 1. CORE CRUD FUNCTIONAL TESTS (MODIFIED FOR NEW FIELDS/LOGIC) ---
class SiteManagementTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!'
        )
        # CRUCIAL ADDITION: Ensure the user's permission is ON for these tests
        self.user.userprofile.can_configure_sites = True
        self.user.userprofile.save()
        
        self.client.login(username=self.user.username, password='SecurePass123!')
        
        self.list_url = reverse('site_list')
        self.create_url = reverse('site_create')
        
        self.site = Site.objects.create(
            name='Test Site',
            url='https://example.com',
            description='A test site',
            is_active=True,
            category='WEB' # ADDED: Category field is now required
        )
        self.edit_url = reverse('site_edit', args=[self.site.pk])
        self.delete_url = reverse('site_delete', args=[self.site.pk])
    
    def test_site_list_loads(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Site')
    
    def test_site_create_page_loads(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Site')
    
    def test_can_create_new_site(self):
        data = {
            'name': 'New Site',
            'url': 'https://newsite.com',
            'description': 'A brand new test site!',
            'is_active': True,
            'category': 'APP' # ADDED: Required 'category' field for POST data
        }
        response = self.client.post(self.create_url, data, follow=True)
        self.assertEqual(Site.objects.count(), 2)
        self.assertContains(response, 'New Site')

    def test_can_edit_existing_site(self):
        data = {
            'name': 'Updated Site',
            'url': 'https://updatedsite.com',
            'description': 'An updated test site!',
            'is_active': False,
            'category': 'DB' # ADDED: Required 'category' field for POST data
        }
        response = self.client.post(self.edit_url, data, follow=True)
        self.site.refresh_from_db()
        self.assertEqual(self.site.name, 'Updated Site')
        self.assertFalse(self.site.is_active)
        self.assertEqual(self.site.category, 'DB') # Test the new field update
        self.assertContains(response, 'Updated Site')
    
    def test_can_delete_site(self):
        response = self.client.post(self.delete_url, follow=True)
        self.assertEqual(Site.objects.count(), 0)
        self.assertContains(response, 'No sites yet.')
        
    def test_unauthenticated_redirect(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


# --- 2. PERMISSION CONTROL (YOUR CORE CONTRIBUTION TEST) ---
class SitePermissionTests(TestCase):
    
    def setUp(self):
        # 1. Setup: User with permissions OFF (The subject of this test)
        self.user_denied = User.objects.create_user(username='denied', password='password')
        self.user_denied.userprofile.can_configure_sites = False # Set to False
        self.user_denied.userprofile.save()
        
        self.create_url = reverse('site_create')
        self.list_url = reverse('site_list')

    def test_site_create_denied_access(self):
        """
        Verifies that a user is blocked from the site_create view 
        if their can_configure_sites permission is False (Custom Security Decorator Test).
        """
        # Log in the user whose permission has been revoked
        self.client.login(username='denied', password='password')
        
        # Attempt to access the creation view (follow=True handles the redirect)
        response = self.client.get(self.create_url, follow=True)
        
        # 1. Assert redirection to the site list page
        self.assertRedirects(response, self.list_url)
        
        # 2. Assert the user receives the correct warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('permission to configure sites' in str(m) for m in messages))
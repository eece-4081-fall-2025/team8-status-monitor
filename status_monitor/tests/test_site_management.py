from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from status_monitor.models import Site

class SiteManagementTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!'
        )
        self.client.login(username=self.user.username,password = 'SecurePass123!')
        
        self.list_url = reverse('site_list')
        self.create_url = reverse('site_create')
        
        self.site = Site.objects.create(
            name = 'Test Site',
            url='https://example.com',
            description= 'A test site',
            is_active = True
        )
        self.edit_url = reverse('site_edit',args=[self.site.pk])
        self.delete_url = reverse('site_delete',args=[self.site.pk])
    
    def test_site_list_loads(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Site')
    
    def test_site_create_page_loads(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Site')
    
    def test_can_create_new_site(self):
        data= {
            'name': 'New Site',
            'url': 'https://newsite.com',
            'description': 'A brand new test site!',
            'is_active': True
        }
        response = self.client.post(self.create_url, data, follow=True)
        self.assertEqual(Site.objects.count(), 2)
        self.assertContains(response, 'New Site')

    def test_can_edit_existing_site(self):
        data = {
            'name': 'Updated Site',
            'url': 'https://updatedsite.com',
            'description': 'An updated test site!',
            'is_active': False 
        }
        response = self.client.post(self.edit_url, data, follow=True)
        self.site.refresh_from_db()
        self.assertEqual(self.site.name, 'Updated Site')
        self.assertFalse(self.site.is_active)
        self.assertContains(response, 'Updated Site')
    
    def test_can_delete_site(self):
        response = self.client.post(self.delete_url, follow=True)
        self.assertEqual(Site.objects.count(), 0)
        self.assertContains(response, 'No sites yet.')
        
    def test_unauthenticated_redirect(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code,302)
        self.assertIn(reverse('login'),response.url)
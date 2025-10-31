from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from status_monitor.models import Site

class SiteManagementTest(TestCase):
    
    def SetUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!'
        )
        self.client.login(username=self.user.username,password = self.user.password)
        
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
            'description': 'A brand new site!',
            'is_active': True
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(Site.objects.count(), 2)
        self.assertContains(response, 'new site')
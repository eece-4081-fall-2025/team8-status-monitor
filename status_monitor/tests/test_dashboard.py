class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()

        # normal user (cannot configure)
        self.user = User.objects.create_user(
            username='homeusertest',
            password='HomePass123!'
        )
        self.user.userprofile.can_configure_sites = False
        self.user.userprofile.save()

        # admin user (can configure)
        self.admin_user = User.objects.create_user(
            username='admin',
            password='SecureAdminPass36!'
        )
        self.admin_user.userprofile.can_configure_sites = True
        self.admin_user.userprofile.save()

        # sample sites
        self.site_up = Site.objects.create(
            name="LocalTest",
            url="http://localhost:8000",
            status="UP",
            is_active=True,
            response_time=10,
        )
        self.site_down = Site.objects.create(
            name="LocalDown",
            url="http://localhost:8001",
            status="DOWN",
            is_active=False,
            response_time=50,
        )

        # urls
        self.home_url = reverse("home")
        self.site_last_url = reverse("site_list")
        self.site_create_url = reverse("site_create")
        self.site_edit_url = reverse("site_edit", args=[self.site_up.pk])
        self.site_delete_url = reverse("site_delete", args=[self.site_up.pk])

    def test_home_page_loads_successfully(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status Monitor")

    def test_site_status_css(self):
        self.client.login(username="homeusertest", password="HomePass123!")
        response = self.client.get(self.home_url)
        self.assertContains(response, 'class="up"')
        self.assertContains(response, 'class="down"')

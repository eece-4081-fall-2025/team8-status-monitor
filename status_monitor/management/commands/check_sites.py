from django.core.management.base import BaseCommand
from status_monitor.models import MonitoredSite, SiteCheckResult
from django.utils import timezone
import requests, time

class Command(BaseCommand):
    help = 'Check the status of monitored sites and log the results.'

    def handle(self, *args, **kwargs):
        monitored_sites = MonitoredSite.objects.all()
        for site in monitored_sites:
            start_time = time.time()
            try:
                response = requests.get(site.url, timeout=10)
                response_time = time.time() - start_time
                is_up = response.status_code == 200
                status_code = response.status_code
            except requests.RequestException:
                response_time = time.time() - start_time
                is_up = False
                status_code = None

            SiteCheckResult.objects.create(
                site=site,
                timestamp=timezone.now(),
                status_code=status_code,
                response_time=response_time,
                is_up=is_up
            )

            self.stdout.write(f"Checked {site.name} ({site.url}): {'UP' if is_up else 'DOWN'}, Response Time: {response_time:.2f}s")
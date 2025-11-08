from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from status_monitor.models import MonitoredSite, SiteCheckResult
import requests, time

def check_sites():
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
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(check_sites, 'interval', minutes=5, name='check_sites_job', jobstore='default')
    scheduler.start()
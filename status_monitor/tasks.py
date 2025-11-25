from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from status_monitor.models import MonitoredSite, SiteCheckResult
import requests, time
from django.db.utils import OperationalError
import sys

scheduler_started = False

MAX_RETRIES = 5

def check_sites():
    monitored_sites = MonitoredSite.objects.all()
    for site in monitored_sites:
        start_time = time.time()
        response_time = None
        response_time = None
        is_up = False
        try:
            response = requests.get(site.url, timeout=10)
            response_time = time.time() - start_time
            is_up = 200 <= response.status_code < 400
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
    global scheduler_started
    if scheduler_started:
        print("⏩ Scheduler already running.")
        return
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            check_sites,
            'interval',
            minutes=5,
            name='check_sites_job',
            replace_existing=True
        )
        if "runserver" in sys.argv:
            scheduler.start()
            scheduler_started = True
            print("✅ APScheduler started successfully!")
    except OperationalError:
        print("⚠️ Database not ready, APScheduler will start after migrations.")
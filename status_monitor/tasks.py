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
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(site.url, timeout=10, headers ={"User-Agent" : "StatusMonitor/1.0"})
                response_time = time.time() - start_time
                status_code = response.status_code
                is_up = 200 <= response.status_code < 400
                break
               
            except requests.Timeout:
                print(f"⏳ Timeout checking {site.url} (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(0.5 * (attempt + 1))

            except requests.ConnectionError:
                print(f"🔌 ConnectionError for {site.url} (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(0.5 * (attempt + 1))

            except requests.exceptions.SSLError:
                print(f"🔐 SSL error for {site.url}")
                break  # retrying won't help SSL errors

            except requests.RequestException as e:
                print(f"⚠️ General HTTP error on {site.url}: {e}")
                time.sleep(0.5 * (attempt + 1))
                
        if response_time is None:
            response_time = time.time() - start_time

            SiteCheckResult.objects.create(
                site=site,
                timestamp=timezone.now(),
                status_code=status_code,
                response_time=response_time,
                is_up=is_up
            )
        print(f"✓ Checked {site.url}: UP={is_up}, status={status_code}, time={response_time:.3f}s")
                
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
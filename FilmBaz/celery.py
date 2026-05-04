import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmBaz.settings')

app = Celery('FilmBaz')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_transport_options={
        "visibility_timeout": 3600,
        "retry_on_timeout": True,
        "max_retries": 20,
        "health_check_interval": 60,
    },
)

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

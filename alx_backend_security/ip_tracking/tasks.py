from celery import shared_task
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    one_hour_ago = timezone.now() - timedelta(hours=1)
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # high request volume
    for item in logs.values('ip_address').annotate(count=Count('id')):
        if item['count'] > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=item['ip_address'],
                reason=f"High request rate: {item['count']} in 1h"
            )

    # sensitive path access
    for log in logs.filter(path__in=['/admin', '/login']):
        SuspiciousIP.objects.get_or_create(
            ip_address=log.ip_address,
            reason=f"Accessed sensitive path {log.path}"
        )

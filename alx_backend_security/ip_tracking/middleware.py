from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from django.core.cache import cache
from django_ipgeolocation.utils import get_client_ip_geolocation


class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)

        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        RequestLog.objects.create(ip_address=ip, path=request.path)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)

        # block check
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # geolocation caching
        geo = cache.get(ip)
        if not geo:
            geo = get_client_ip_geolocation(ip)
            cache.set(ip, geo, 86400)  # 24h cache

        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            country=geo.get('country_name'),
            city=geo.get('city')
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
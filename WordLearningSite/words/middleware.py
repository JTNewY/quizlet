from django.http import HttpResponseForbidden

class IPRestrictMiddleware:
    ALLOWED_IPS = ['121.172.80.1']  # 여기에 허용할 IP 주소를 추가하세요.

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        if ip_address not in self.ALLOWED_IPS:
            return HttpResponseForbidden("Access denied")
        return self.get_response(request)
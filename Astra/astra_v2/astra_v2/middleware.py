from django.http import JsonResponse
from django.contrib.auth import authenticate
from IDS.ids_core import IDS
from alert_bot.notify import send_notification
import threading

ids = IDS(alert_func=send_notification)
_request_local = threading.local()

class AuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/accounts/login/' and request.method == "POST":
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            username = request.POST.get('username', 'unknown')
            print(f"[DEBUG] Логин пользователя: {username}, IP: {ip}")

            # Проверка на блокировку IP
            allowed, local_end_time = ids.detect_failed_logins(ip, username)
            if not allowed:
                print(f"[DEBUG] IP временно заблокирован до {local_end_time}")
                return JsonResponse({
                    "error": f"Ваш IP временно заблокирован до {local_end_time} из-за подозрительной активности."
                }, status=403)
            # Не РОССИЯ
            if not ids.check_ip_geolocation(ip):
                print("[DEBUG] Доступ запрещён из-за геолокации")
                return JsonResponse({"error": "Доступ запрещён. Ваш IP не соответствует российской геолокации."}, status=403)

        return self.get_response(request)

class CurrentRequestMiddleware:
    """Middleware для сохранения текущего запроса в потоке."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_local.request = request
        response = self.get_response(request)
        return response

def get_current_request():
    """Получение текущего запроса."""
    current_request = getattr(_request_local, 'request', None)
    print(f"[DEBUG] Текущий запрос: {current_request}")  # Отладка
    return current_request
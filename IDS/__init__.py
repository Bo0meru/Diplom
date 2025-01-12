from collections import defaultdict

class IDS:
    def __init__(self, alert_func=None, report_func=None):
        self.alerts = []  # Логи предупреждений
        self.user_activity = defaultdict(list)  # Мониторинг активности пользователей
        self.blocked_ips = set()  # Список заблокированных IP-адресов
        self.failed_attempts = defaultdict(int)  # Счетчик неудачных попыток входа
        self.alert_func = alert_func  # Функция для отправки критических уведомлений
        self.report_func = report_func  # Функция для отправки отчетов

import logging
import os
import time
from collections import defaultdict
from datetime import datetime

# Настройка логирования с поддержкой UTF-8
log_path = os.path.join(os.path.dirname(__file__), 'ids_log.log')
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')

class IDS:
    def __init__(self):
        self.alerts = []  # Логи предупреждений
        self.user_activity = defaultdict(list)  # Мониторинг активности пользователей
        self.blocked_ips = set()  # Список заблокированных IP-адресов

    # 1. Логирование событий
    def log_event(self, user, action):
        event = f"Пользователь: {user}, Действие: {action}"
        logging.info(event)
        print(f"Logging event: {event}")  # Выводим событие для проверки
        self.alerts.append(event)
    
    # 2. Обнаружение подозрительной активности на основе частоты действий
    def track_activity(self, user):
        now = time.time()
        self.user_activity[user].append(now)

        # Фильтрация событий за последние 60 секунд
        recent_activity = [t for t in self.user_activity[user] if now - t < 60]
        self.user_activity[user] = recent_activity

        if len(recent_activity) > 10:
            self.log_event(user, "Высокая частота действий")
    
    # 3. Проверка IP и устройства пользователя
    def check_location_device(self, user, current_ip, current_device):
        past_ip = user.get("last_ip")
        past_device = user.get("last_device")

        if current_ip != past_ip or current_device != past_device:
            self.log_event(user["name"], "Подозрительный вход с нового устройства или IP")
        
        # Обновление данных пользователя
        user["last_ip"] = current_ip
        user["last_device"] = current_device
    
    # 4. Детекция множества неудачных попыток входа
    def detect_failed_logins(self, user):
        if user.get("failed_attempts", 0) > 5:
            self.log_event(user["name"], "Блокировка после множества неудачных попыток входа")
    
    # 5. Блокировка подозрительного IP
    def block_ip(self, ip_address):
        self.blocked_ips.add(ip_address)
        self.log_event(ip_address, "IP заблокирован из-за подозрительной активности")

    def check_ip(self, ip_address):
        if ip_address in self.blocked_ips:
            return "Доступ запрещён"
        return "Доступ разрешён"
    
    # 6. Создание отчёта
    def generate_daily_report(self):
        report_path = os.path.join(os.path.dirname(__file__), "daily_report.txt")
        with open(report_path, "w", encoding="utf-8") as report_file:
            for event in self.alerts:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                report_file.write(f"{timestamp} - {event}\n")
                print(f"Writing to report: {timestamp} - {event}")  # Выводим для проверки
        print(f"Отчет создан: {report_path}")


# Пример использования IDS
if __name__ == "__main__":
    ids = IDS()
    
    # Тест 1: Логирование событий
    ids.log_event("test_user", "Вход в систему")

    # Тест 2: Частая активность
    for _ in range(12):
        ids.track_activity("test_user")
        time.sleep(0.1)

    # Тест 3: Проверка IP и устройства
    test_user = {"name": "test_user", "last_ip": "192.168.1.1", "last_device": "PC"}
    ids.check_location_device(test_user, "192.168.1.2", "Laptop")

    # Тест 4: Неудачные попытки входа
    test_user["failed_attempts"] = 6
    ids.detect_failed_logins(test_user)

    # Тест 5: Блокировка IP
    ids.block_ip("192.168.1.100")
    print(ids.check_ip("192.168.1.100"))  # Ожидается: Доступ запрещён
    print(ids.check_ip("192.168.1.101"))  # Ожидается: Доступ разрешён

    # Тест 6: Генерация отчёта
    ids.generate_daily_report()

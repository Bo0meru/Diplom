import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Настройка логирования с поддержкой UTF-8
log_path = os.path.join(os.path.dirname(__file__), 'ids_log.log')
logging.basicConfig(
    filename=log_path, 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s', 
    encoding='utf-8'
)

class IDS:
    def __init__(self, alert_func=None, report_func=None):
        self.alerts = []  # Логи предупреждений
        self.user_activity = defaultdict(list)  # Мониторинг активности пользователей
        self.blocked_ips = set()  # Список заблокированных IP-адресов
        self.alert_func = alert_func  # Функция для отправки критических уведомлений
        self.report_func = report_func  # Функция для отправки отчетов

    # 1. Логирование событий
    def log_event(self, user, action, critical=False):
        event = f"Пользователь: {user}, Действие: {action}"
        logging.info(event)
        self.alerts.append(event)
        print(f"Logging event: {event}")

        # Отправка критического уведомления
        if critical and self.alert_func:
            print(f"[DEBUG] Отправка критического уведомления: {event}")
            self.alert_func(event)
            print("[DEBUG] Уведомление отправлено")

    # 2. Обнаружение подозрительной активности на основе частоты действий
    def track_activity(self, user):
        now = time.time()
        self.user_activity[user].append(now)

        # Фильтрация событий за последние 60 секунд
        recent_activity = [t for t in self.user_activity[user] if now - t < 60]
        self.user_activity[user] = recent_activity

        if len(recent_activity) > 10:
            self.log_event(user, "Высокая частота действий", critical=True)
            if self.alert_func:
                print(f"[DEBUG] Уведомление: Высокая частота действий от пользователя {user}")
                self.alert_func(f"Подозрительная активность: высокая частота действий от пользователя {user}")

    # 3. Проверка IP и устройства пользователя
    def check_location_device(self, user, current_ip, current_device):
        past_ip = user.get("last_ip")
        past_device = user.get("last_device")

        if current_ip != past_ip or current_device != past_device:
            self.log_event(user["name"], "Подозрительный вход с нового устройства или IP", critical=True)
            if self.alert_func:
                print(f"[DEBUG] Уведомление: Подозрительный вход для пользователя {user['name']}")
                self.alert_func(f"Подозрительный вход: новый IP или устройство для пользователя {user['name']}")
        
        # Обновление данных пользователя
        user["last_ip"] = current_ip
        user["last_device"] = current_device

    # 4. Детекция множества неудачных попыток входа
    def detect_failed_logins(self, user):
        if user.get("failed_attempts", 0) > 5:
            self.log_event(user["name"], "Блокировка после множества неудачных попыток входа", critical=True)
            if self.alert_func:
                print(f"[DEBUG] Уведомление: Блокировка пользователя {user['name']} после неудачных попыток")
                self.alert_func(f"Блокировка пользователя {user['name']} после множества неудачных попыток входа")

    # Проверка загружаемого файла
    def verify_file(self, user, file_name, mime_type):
        # Запись в лог о загрузке файла
        self.log_event(user, f"Файл {file_name} успешно записан во временную папку")
        
        # Проверка допустимых MIME-типов
        allowed_mime_types = ["application/pdf", "image/jpeg", "image/png"]
        if mime_type not in allowed_mime_types:
            # Если тип неверный, записываем события в логи и отправляем критическое уведомление
            self.log_event(user, f"Недопустимый MIME-тип или расширение: {mime_type}, {os.path.splitext(file_name)[1]}", critical=True)
            self.log_event(user, "Файл не прошел проверку безопасности.", critical=True)
            if self.alert_func:
                print(f"[DEBUG] Уведомление: Файл не прошел проверку безопасности для пользователя {user}")
                self.alert_func(f"Файл не прошел проверку безопасности для пользователя {user}")
            return False
        
        # Если тип верный, запись об успешной проверке
        self.log_event(user, f"Файл {file_name} успешно прошел проверку безопасности")
        return True 

    # 5. Блокировка подозрительного IP
    def block_ip(self, ip_address):
        self.blocked_ips.add(ip_address)
        self.log_event(ip_address, "IP заблокирован из-за подозрительной активности", critical=True)
        if self.alert_func:
            print(f"[DEBUG] Уведомление: IP-адрес {ip_address} заблокирован из-за подозрительной активности")
            self.alert_func(f"IP-адрес {ip_address} заблокирован из-за подозрительной активности")

    def check_ip(self, ip_address):
        if ip_address in self.blocked_ips:
            return "Доступ запрещён"
        return "Доступ разрешён"


 # 6. Создание отчёта за указанный период
    def generate_report(self, start_time=None, end_time=None):
        report_path = os.path.join(os.path.dirname(__file__), "daily_report.txt")
        
        # Проверка наличия лог-файла
        if not os.path.exists(log_path):
            print("[ERROR] Лог-файл отсутствует. Отчет не может быть создан.")
            return None

        # Установка значений времени по умолчанию, если они не указаны
        if not start_time:
            start_time = datetime.combine(datetime.now(), datetime.min.time())
        if not end_time:
            end_time = datetime.combine(datetime.now() + timedelta(days=1), datetime.min.time())

        # Запись данных в отчет
        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write(f"Отчет IDS с {start_time} по {end_time}\n\n")
            with open(log_path, "r", encoding="utf-8") as log_file:
                for line in log_file:
                    try:
                        log_time = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
                        if start_time <= log_time < end_time:
                            report_file.write(line)
                            print(f"Writing to report: {line.strip()}")  # Для проверки выводим в консоль
                    except ValueError:
                        # Игнорируем строки, не соответствующие формату даты
                        print(f"[WARNING] Неправильный формат строки лога: {line.strip()}")

            print(f"Отчет создан: {report_path}")

        # Отправка отчета, если функция указана
        if self.report_func and start_time == datetime.combine(datetime.now(), datetime.min.time()):
            self.report_func(report_path)  # Отправка отчета только один раз

        return report_path

    def schedule_daily_report(self):
        """Запланированная отправка ежедневного отчёта в 08:00 через Telegram."""
        report_path = self.generate_report()
        if self.report_func:
            self.report_func(report_path)
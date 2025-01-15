import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from alert_bot.notify import send_notification
from flask import Flask, request, jsonify
from collections import defaultdict
import geoip2.database
from datetime import datetime, timedelta
import threading
from multiprocessing import Process
from threading import Lock
import pytz


MOSCOW_TZ = pytz.timezone("Europe/Moscow")
# Настройка логирования с поддержкой UTF-8
log_path = os.path.join(os.path.dirname(__file__), 'ids_log.log')
logging.basicConfig(
    filename=log_path, 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s', 
    encoding='utf-8'
)


class IDS:
    
    def __init__(self, geoip_db_path=None, alert_func=None, report_func=None):
        # Указание пути по умолчанию на основе текущей папки
        if geoip_db_path is None:
            geoip_db_path = os.path.join(os.path.dirname(__file__), 'GeoLite2-Country.mmdb')

        # Проверка существования файла
        if not os.path.exists(geoip_db_path):
            raise FileNotFoundError(f"GeoLite2-Country.mmdb not found at {geoip_db_path}")
        print(f"GeoLite2-Country.mmdb expected at: {geoip_db_path}")
        self.geoip_reader = geoip2.database.Reader(geoip_db_path)
        self.alert_func = alert_func
        self.report_func = report_func
        self.alerts = []
        self.lock = Lock()
        self.blocked_ips = {}
        self.user_activity = defaultdict(list)
        self.failed_attempts = defaultdict(int)
        self.block_duration = timedelta(seconds=10)  # Длительность блокировки
        self._start_cleanup_task()


    def _start_cleanup_task(self):
        """Запуск фоновой задачи для очистки истёкших блокировок."""
        def cleanup_blocked_ips():
            while True:
                now_time = datetime.now(pytz.UTC)
                # now_time = now()  # Используем django.utils.timezone.now()
                # print(f"[DEBUG] Сейчас {now_time}, проверка истёкших блокировок...")
                with self.lock:  # Защищаем доступ к shared-ресурсам
                    expired_ips = [ip for ip, end_time in self.blocked_ips.items() if now_time > end_time]

                if expired_ips:  # Если есть разблокированные IP
                    logging.info(
                        f"[DEBUG] {len(expired_ips)} IP-адресов разблокировано в {now_time.strftime('%Y-%m-%d %H:%M:%S')}. Список: {', '.join(expired_ips)}"
                    )

                for ip in expired_ips:
                    del self.blocked_ips[ip]
                    if ip in self.failed_attempts:
                        del self.failed_attempts[ip]
                    print(f"[DEBUG] Срок блокировки IP {ip} истёк. Разблокировка и сброс счётчика.")
                time.sleep(10)  # Проверяем каждые 10 секунд - Изменить на 30

        # Создаём поток для фоновой задачи
        cleanup_thread = threading.Thread(target=cleanup_blocked_ips, daemon=True)
        cleanup_thread.start()


    #Логирование событий
    def log_event(self, user, action, critical=False, ip="unknown"):
        event = f"Пользователь: {user}, Действие: {action}"
        logging.info(event)
        self.alerts.append(event)
        print(f"Logging event: {event}")

        # Отправка критического уведомления
        if critical and self.alert_func:
            logging.info(f"Отправка критического уведомления\n {event}")
            print(f"[DEBUG] Отправка критического уведомления: {event}")
            self.alert_func(
                user=user,
                ip=ip,
                action=action,
                result="Критическое событие"
            )
    # 1. Проверка блока IP
    def check_ip(self, ip_address):
        if ip_address in self.blocked_ips:
            end_time = self.blocked_ips[ip_address]
            now = datetime.utcnow()
            if now() < end_time:
                logging.info(f"IP {ip_address} заблокирован до {end_time}")
                print(f"[DEBUG] IP {ip_address} заблокирован до {end_time}")
                return "Доступ запрещён"
            else:
                # Сброс блокировки и счётчика неудачных попыток
                del self.blocked_ips[ip_address]
                if ip_address in self.failed_attempts:
                    del self.failed_attempts[ip_address]
                logging.info(f"Срок блокировки IP {ip_address} истёк. Разблокировка.")    
                print(f"[DEBUG] Срок блокировки IP {ip_address} истёк. Разблокировка.")
        return "Доступ разрешён"



    # 0. Геолокация
    def check_ip_geolocation(self, ip_address):
        try:
            response = self.geoip_reader.country(ip_address)
            country_code = response.country.iso_code
            if country_code != "RU":
                self.block_ip(ip_address)
                self.log_event(
                    user="unknown",
                    action=f"Блокировка IP {ip_address} (не российский IP)",
                    critical=True,
                    ip=ip_address
                )
                logging.info(f"Блокировка IP {ip_address} (не российский IP)")
                return False  # Блокировать доступ
        except geoip2.errors.AddressNotFoundError:
            self.log_event(
                user="unknown",
                action=f"IP {ip_address} не найден в базе GeoIP",
                critical=True,
                ip=ip_address
            )
            logging.info(f"IP {ip_address} не найден в базе GeoIP. НЕОБХОДИМ АНАЛИЗ")
        return True  # Разрешить доступ

    # 2. Обнаружение подозрительной активности на основе частоты действий
    def track_activity(self, user):
        now = datetime.utcnow()

        # Добавляем текущую временную отметку
        self.user_activity[user].append(now)
        # Фильтрация событий за последние 60 секунд
        recent_activity = [t for t in self.user_activity[user] if (now - t).total_seconds() < 60]
        self.user_activity[user] = recent_activity

        if len(recent_activity) > 15:
            self.log_event(user, "Высокая частота действий", critical=True)
            if self.alert_func:
                print(f"[DEBUG] Уведомление: Высокая частота действий от пользователя {user}")
                self.alert_func(f"Подозрительная активность: высокая частота действий от пользователя {user}")
                logging.info(f"Уведомление: Высокая частота действий от пользователя {user}")

    # 3. Проверка IP и устройства пользователя
    def check_location_device(self, user, current_ip, current_device):
        past_ip = user.get("last_ip")
        past_device = user.get("last_device")

        if current_ip != past_ip or current_device != past_device:
            self.log_event(user["name"], "Подозрительный вход с нового устройства или IP", critical=True)
            if self.alert_func:
                print(f"[DEBUG] Уведомление: Подозрительный вход для пользователя {user['name']}")
                self.alert_func(f"Подозрительный вход: новый IP или устройство для пользователя {user['name']}")
                logging.info(f"Уведомление: Подозрительный вход для пользователя {user['name']}")
        
        # Обновление данных пользователя
        user["last_ip"] = current_ip
        user["last_device"] = current_device

    # 4. Детекция множества неудачных попыток входа
    def detect_failed_logins(self, ip, username):
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = 0
        self.failed_attempts[ip] += 1

        if self.failed_attempts[ip] > 3:  # Увеличьте лимит до нужного значения
            now_time = datetime.now(pytz.UTC)
            end_time = now_time + self.block_duration
            self.blocked_ips[ip] = end_time
            local_end_time = end_time.astimezone(MOSCOW_TZ).strftime('%Y-%m-%d %H:%M:%S')
            local_end_time = end_time.astimezone(MOSCOW_TZ).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[DEBUG] Блокировка IP {ip} до {local_end_time}")
            self.log_event(username, f"Превышено количество попыток входа. Блокировка до {local_end_time}.", ip=ip, critical=True)
            return False, local_end_time


        # Сбрасываем счётчик, если блокировка истекла
        if ip in self.blocked_ips and now_time() > self.blocked_ips[ip]:
            print(f"[DEBUG] Сброс счётчика неудачных попыток для IP {ip}")
            del self.failed_attempts[ip]

        return True, None




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
    def block_ip(self, ip_address, user="unknown"):
        now_time = datetime.now(pytz.UTC)
        end_time = self.blocked_ips.get(ip_address, now_time + self.block_duration)
        self.blocked_ips[ip_address] = end_time
        local_end_time = end_time.astimezone(MOSCOW_TZ).strftime('%Y-%m-%d %H:%M:%S')
        event = f"IP {ip_address} заблокирован из-за подозрительной активности до {local_end_time}"
        print("[DEBUG] Отправка уведомления через alert_func")
        self.log_event(
                user=user,
                critical=True,
                ip=ip_address,
                action=f"IP {ip_address} временно заблокирован до {local_end_time}"
            )      

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


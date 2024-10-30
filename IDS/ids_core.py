# O:\Diplom\IDS\ids_core.py

import logging
import os
from datetime import datetime

# Настройка логгирования для IDS
log_path = os.path.join(os.path.dirname(__file__), 'ids_log.log')
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(message)s')

class IDS:
    def __init__(self):
        self.alerts = []

    def log_event(self, user, action):
        event = f"User: {user}, Action: {action}"
        logging.info(event)
        self.alerts.append(event)

    def detect_anomalies(self, user, activity_type):
        if activity_type == "failed_login" and user.failed_attempts > 5:
            self.log_event(user, "Suspicious login activity detected")
            return True
        return False
    
    def send_alert(self, message):
      # Функция для отправки email или записи уведомления
      print(f"ALERT: {message}")

    def generate_report(self):
    # Создание отчета по событиям
      with open("audit_report.csv", "w") as file:
          file.write("User, Action, Time\n")
          for event in self.alerts:
              file.write(event + "\n")

    def adapt_access(self, user):
      # Проверка активности и адаптация доступа
      if self.detect_anomalies(user, "suspicious_activity"):
          user.access_level = "restricted"
          self.send_alert(f"Access level changed for {user}")
          
# Пример использования IDS
if __name__ == "__main__":
    ids = IDS()
    ids.detect_anomaly("suspicious_activity")

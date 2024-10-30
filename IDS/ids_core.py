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

    def log_event(self, event):
        logging.info(f'Event logged: {event}')
        self.alerts.append(event)

    def detect_anomaly(self, activity):
        # Пример функции, анализирующей действия пользователя
        if activity == "suspicious_activity":
            self.log_event("Suspicious activity detected!")
        return activity

# Пример использования IDS
if __name__ == "__main__":
    ids = IDS()
    ids.detect_anomaly("suspicious_activity")

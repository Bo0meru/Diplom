#Запуск через: python -m alert_bot.test_send
from alert_bot.telegram_bot import send_telegram_alert, send_daily_report
from datetime import datetime, timedelta
import os

# Тестовое сообщение критического уведомления
def test_alert():
    test_message = "Тестовое критическое уведомление от IDS."
    send_telegram_alert(test_message)

# Тестовый отчет для отправки
def test_report():
    # Создание временного отчета для теста
    report_path = "test_report.txt"
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()

    # Запись тестового содержимого в отчет
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(f"Тестовый отчет IDS с {start_time} по {end_time}\n")
        file.write("Тестовая запись: Все системы работают нормально.\n")

    # Отправка тестового отчета
    send_daily_report(report_path)

    # Удаление тестового файла отчета
    os.remove(report_path)

if __name__ == "__main__":
    print("Отправка тестового критического уведомления...")
    test_alert()
    print("Отправка тестового отчета...")
    test_report()

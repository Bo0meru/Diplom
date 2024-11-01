import requests

TELEGRAM_TOKEN = "7952577888:AAGNa6iCvQJdjsanN2jEpofHJ9YlqBtZtk4"
ADMIN_CHAT_ID = "1244056790"


def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": f"Тестовое уведомление IDS:\n{message}"}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("[INFO] Уведомление успешно отправлено в Telegram.")
        else:
            print(f"[ERROR] Ошибка при отправке уведомления: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Ошибка при выполнении запроса: {e}")

# Тестовый вызов
send_telegram_alert("Проверка отправки критического уведомления")

import requests
from alert_bot.config import TELEGRAM_TOKEN, ADMIN_CHAT_ID

def send_notification(user, ip, action, result):
    message = (
        f"Уведомление от IDS:\n"
        f"Пользователь: {user}\n"
        f"IP: {ip}\n"
        f"Действие: {action}\n"
        f"Событие: {result}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("[INFO] Уведомление успешно отправлено в Telegram.")
        else:
            print(f"[ERROR] Ошибка отправки уведомления: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Ошибка при выполнении запроса: {e}")

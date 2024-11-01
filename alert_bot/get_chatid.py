import requests
from alert_bot.config import TELEGRAM_TOKEN, ADMIN_CHAT_ID

TELEGRAM_TOKEN = "7952577888:AAGNa6iCvQJdjsanN2jEpofHJ9YlqBtZtk4"
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

response = requests.get(url)
data = response.json()

# Найдите chat_id в ответе
for update in data['result']:
    print(update['message']['chat']['id'])

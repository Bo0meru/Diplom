import asyncio
import schedule
import time
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
from IDS.ids_core import IDS
from alert_bot.config import TELEGRAM_TOKEN, ADMIN_CHAT_ID

# Настройка логирования с особым форматированием для сообщений из alert_bot
log_file_path = "IDS/ids_log.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def log_alert_bot(message):
    """Добавляет специальный раздел в лог для alert_bot сообщений."""
    logging.info("********       ALERT_BOT        ********")

log_alert_bot("=== Запуск программы бота ===")

# Функции для отправки уведомлений и отчетов
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": f"Критическое уведомление IDS:\n{message}"}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("[INFO] Уведомление успешно отправлено в Telegram.")
            logging.info("Уведомление успешно отправлено в Telegram.")
        else:
            print(f"[ERROR] Ошибка при отправке уведомления: {response.status_code} - {response.text}")
            logging.error(f"Ошибка при отправке уведомления: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"[ERROR] Ошибка при подключении к Telegram API: {e}")
        logging.error(f"Ошибка при подключении к Telegram API: {e}")



def send_daily_report(report_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(report_path, "rb") as report_file:
        files = {"document": report_file}
        data = {"chat_id": ADMIN_CHAT_ID, "caption": "Ежедневный отчет IDS"}
        response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        logging.info("Отчет успешно отправлен в Telegram.")
    else:
        logging.error(f"Ошибка при отправке отчета: {response.text}")

# Инициализация IDS с функциями для критических уведомлений и отчетов
ids = IDS(alert_func=send_telegram_alert, report_func=send_daily_report)

async def report(update: Update, context: CallbackContext):
    try:
        user = update.message.from_user
        logging.info(f"Получен запрос от пользователя {user.id} ({user.username}): {update.message.text}")
        
        start_str, end_str = context.args[0], context.args[1]
        
        start_time = datetime.strptime(start_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        end_time = datetime.strptime(end_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        report_path = ids.generate_report(start_time, end_time)

        if report_path:
            send_daily_report(report_path)
            await update.message.reply_text("Отчет отправлен.")
            logging.info(f"Отчет за период {start_time} - {end_time} успешно отправлен пользователю {user.id}.")
        else:
            await update.message.reply_text("За указанный период нет данных для отчета.")
            logging.info(f"Отчет за период {start_time} - {end_time} не был сгенерирован, данных нет.")

    except Exception as e:
        await update.message.reply_text("Ошибка: Проверьте формат дат (YYYY-MM-DD).")
        logging.error(f"Ошибка при обработке запроса отчета от пользователя {user.id}: {e}")

async def main():
    # Создаем приложение бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    await application.initialize()

    # Команда /report
    application.add_handler(CommandHandler("report", report))

    # Ежедневная автоотправка в 08:00
    schedule.every().day.at("08:00").do(ids.schedule_daily_report)

    # Запуск бота
    logging.info("=== Запуск программы бота ===")
    try:
        await application.start()
        await application.updater.start_polling()  # Запускаем polling

        while True:
            schedule.run_pending()
            await asyncio.sleep(60)
    except Exception as e:
        logging.error(f"[ERROR] Ошибка при выполнении: {e}")
    finally:
        await application.stop()
        await application.shutdown()
        logging.info("=== Остановка программы бота ===")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logging.error(f"Ошибка запуска основного цикла: {e}")
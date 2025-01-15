from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Question, Answer, Tag
from IDS import ids_core
from django.contrib.auth.models import User
from astra_v2.middleware import get_current_request
import json
import random
import string
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
import logging
from alert_bot.notify import send_notification

ids = ids_core.IDS
# Храним активность пользователей
user_activity_log = {}


def get_user_and_ip():
    """
    Получение текущего пользователя и IP-адреса из запроса.
    """
    request = get_current_request()  # Получаем текущий запрос
    if not request:
        return "unknown", "unknown"
    user = getattr(request, "user", None) or "unknown"
    ip = request.META.get("REMOTE_ADDR", "unknown")
    return user, ip


def log_user_activity(user, ip):
    """
    Логирует активность пользователя и проверяет частоту изменений.
    """
    current_time = now()
    if ip not in user_activity_log:
        user_activity_log[ip] = []

    # Добавляем текущую временную метку
    user_activity_log[ip].append(current_time)

    # Фильтруем записи только за последнюю минуту
    user_activity_log[ip] = [
        timestamp for timestamp in user_activity_log[ip]
        if (current_time - timestamp).total_seconds() <= 60
    ]

    # Проверяем, превышена ли частота
    if len(user_activity_log[ip]) > 10:
        return True  # Блокировать IP

    return False

# Глобальный список заблокированных IP-адресов (для предотвращения повторной блокировки)
blocked_ips = set()

def block_ip_and_reset_password(user, ip):
    """
    Блокирует IP и сбрасывает пароль пользователя.
    """
    global blocked_ips

    # Проверяем, заблокирован ли уже IP-адрес
    if ip in blocked_ips:
        logging.info(f"Попытка повторной блокировки IP {ip} предотвращена.")
        return

    # Добавляем IP-адрес в список заблокированных
    blocked_ips.add(ip)

    # Блокировка IP
    if isinstance(user, User) and user != "unknown":
        ids.block_ip(ip, user=user.username)

    # Генерация нового пароля
    new_password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    if isinstance(user, User) and user != "unknown":
        user.set_password(new_password)
        user.save()

    # Логирование события
    notification_text = (
        f"Блокировка IP {ip} за частые изменения данных.\n"
        f"Пользователь: {user.username if user != 'unknown' else 'unknown'}\n"
        f"Новый пароль: {new_password}\n"
        f"Результат IDS: Пароль сброшен и IP заблокирован"
    )
    ids.log_event(
        user=user.username if user != "unknown" else "unknown",
        ip=ip,
        action="Частое изменение данных",
        critical=True
    )
    ids.alert_func(
        user=user.username if user != "unknown" else "unknown",
        ip=ip,
        action="Частое изменение данных",
        result=notification_text
    )
    logging.info(f"Частое изменение данных.\n {notification_text}.")

def check_and_log_user_activity(user, ip):
    """
    Проверяет частоту действий пользователя и вызывает блокировку при необходимости.
    """
    if log_user_activity(user, ip):  # Если частота превышена
        block_ip_and_reset_password(user, ip)
        return True  # Заблокировано
    return False  # Действие допустимо

# Логирование активности пользователя и проверка частоты
def log_user_activity(user, ip):
    """
    Логирует действия пользователя и проверяет частоту изменений.
    """
    current_time = now()
    if ip not in user_activity_log:
        user_activity_log[ip] = []

    # Добавляем временную метку текущего действия
    user_activity_log[ip].append(current_time)

    # Удаляем старые записи (старше 60 секунд)
    user_activity_log[ip] = [
        timestamp for timestamp in user_activity_log[ip]
        if (current_time - timestamp).total_seconds() <= 60
    ]

    # Проверяем частоту действий
    if len(user_activity_log[ip]) > 10:  # Условие превышения частоты
        return True
    return False

# Универсальный вызов проверки в каждом обработчике
@receiver(pre_save, sender=Question)
def track_question_changes(sender, instance, **kwargs):
    if instance.pk:
        user, ip = get_user_and_ip()
        if check_and_log_user_activity(user, ip):  # Проверка частоты действий
            return

        try:
            old_instance = Question.objects.get(pk=instance.pk)
            if instance.text != old_instance.text:
                notification_text = (
                    f"Изменение текста вопроса №{instance.id}\n"
                    f"Старый текст: {old_instance.text}\n"
                    f"Новый текст: {instance.text}\n"
                    f"Результат IDS: Подтвердить изменения."
                )
                ids.log_event(
                    user=user.username if user != "unknown" else "unknown",
                    ip=ip,
                    action=notification_text,
                    critical=True
                )
        except Question.DoesNotExist:
            pass


@receiver(pre_save, sender=Answer)
def track_answer_changes(sender, instance, **kwargs):
    if instance.pk:
        user, ip = get_user_and_ip()
        if check_and_log_user_activity(user, ip):  # Проверка частоты действий
            return

        try:
            old_instance = Answer.objects.get(pk=instance.pk)
            changes = []
            if instance.text != old_instance.text:
                changes.append(f"Текст ответа: {old_instance.text} -> {instance.text}")
            if instance.correct != old_instance.correct:
                changes.append(f"Флаг 'Верный ответ': {old_instance.correct} -> {instance.correct}")

            if changes:
                notification_text = (
                    f"Изменение ответа к вопросу №{instance.question.id}\n"
                    + "\n".join(changes)
                    + f"\nРезультат IDS: Подтвердить изменения."
                )
                ids.log_event(
                    user=user.username if user != "unknown" else "unknown",
                    ip=ip,
                    action=notification_text,
                    critical=True
                )
        except Answer.DoesNotExist:
            pass


@receiver(m2m_changed, sender=Question.tags.through)
def track_tag_changes(sender, instance, action, pk_set, **kwargs):
    user, ip = get_user_and_ip()
    if check_and_log_user_activity(user, ip):  # Проверка частоты действий
        return

    if action == "post_add":
        added_tags = [str(tag) for tag in Tag.objects.filter(pk__in=pk_set)]
        notification_text = (
            f"Добавление меток к вопросу №{instance.id}\n"
            f"Метки: {', '.join(added_tags)}\n"
            f"Результат IDS: Метки добавлены."
        )
        ids.log_event(
            user=user.username if user != "unknown" else "unknown",
            ip=ip,
            action=notification_text,
            critical=True
        )
    elif action == "post_remove":
        removed_tags = [str(tag) for tag in Tag.objects.filter(pk__in=pk_set)]
        notification_text = (
            f"Удаление меток у вопроса №{instance.id}\n"
            f"Метки: {', '.join(removed_tags)}\n"
            f"Результат IDS: Метки удалены."
        )
        ids.log_event(
            user=user.username if user != "unknown" else "unknown",
            ip=ip,
            action=notification_text,
            critical=True
        )


ids = ids(alert_func=send_notification)


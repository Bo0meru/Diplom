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


def block_ip_and_reset_password(user, ip):
    """
    Блокирует IP и сбрасывает пароль пользователя.
    """
    # Блокировка IP
    ids.block_ip(ip, user=user.username if user != "unknown" else "unknown")

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


# 1. Проверка на изменение названия вопроса
@receiver(pre_save, sender=Question)
def track_question_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Question.objects.get(pk=instance.pk)
            if instance.text != old_instance.text:
                user, ip = get_user_and_ip()

                # Логирование активности
                if log_user_activity(user, ip):
                    block_ip_and_reset_password(user, ip)
                    return

                # Обычное логирование изменений
                notification_text = (
                    f"Изменение структуры БД: Таблица 'Вопросы'\n"
                    f"Вопрос №: {instance.id}\n"
                    f"Наименование вопроса: {old_instance.text} -> {instance.text}\n"
                    f"Результат IDS: Подтвердить изменение наименования. Сохранить вопрос"
                )
                ids.log_event(
                    user=user.username if user != "unknown" else "unknown",
                    ip=ip,
                    action=notification_text,
                    critical=True
                )
                logging.info(f"ТАБЛИЦА ВОПРОСОВ.\n {notification_text}.")
        except Question.DoesNotExist:
            pass


# 2. Проверка на добавление нового ответа
@receiver(post_save, sender=Answer)
def track_new_answers(sender, instance, created, **kwargs):
    if created:
        user, ip = get_user_and_ip()

        # Логирование активности
        if log_user_activity(user, ip):
            block_ip_and_reset_password(user, ip)
            return

        notification_text = (
            f"Добавление ответа к вопросу №{instance.question.id} ({instance.question.text})\n"
            f"Текст ответа: {instance.text}\n"
            f"Верный ответ: {'Да' if instance.correct else 'Нет'}\n"
            f"Результат IDS: Сохранить"
        )
        ids.log_event(
            user=user.username if user != "unknown" else "unknown",
            ip=ip,
            action=notification_text,
            critical=True
        )
        logging.info(f"ТАБЛИЦА ОТВЕТОВ.\n {notification_text}.")


# 3. Проверка на удаление ответа
@receiver(post_delete, sender=Answer)
def track_deleted_answers(sender, instance, **kwargs):
    user, ip = get_user_and_ip()

    # Логирование активности
    if log_user_activity(user, ip):
        block_ip_and_reset_password(user, ip)
        return

    notification_text = (
        f"Удаление ответа из вопроса №{instance.question.id} ({instance.question.text})\n"
        f"Текст ответа: {instance.text}\n"
        f"Верный ответ: {'Да' if instance.correct else 'Нет'}\n"
        f"Результат IDS: Подтвердить удаление"
    )
    ids.log_event(
        user=user.username if user != "unknown" else "unknown",
        ip=ip,
        action=notification_text,
        critical=True
    )
    logging.info(f"ТАБЛИЦА ОТВЕТОВ.\n {notification_text}.")


# 4. Проверка на добавление или удаление меток
@receiver(m2m_changed, sender=Question.tags.through)
def track_tag_changes(sender, instance, action, pk_set, **kwargs):
    user, ip = get_user_and_ip()

    # Логирование активности
    if log_user_activity(user, ip):
        block_ip_and_reset_password(user, ip)
        return

    if action == "post_add":
        added_tags = [str(tag) for tag in Tag.objects.filter(pk__in=pk_set)]
        notification_text = (
            f"Добавление меток к вопросу №{instance.id} ({instance.text})\n"
            f"Метки: {', '.join(added_tags)}\n"
            f"Результат IDS: Метки добавлены"
        )
        ids.log_event(
            user=user.username if user != "unknown" else "unknown",
            ip=ip,
            action=notification_text,
            critical=True
        )
        logging.info(f"ТАБЛИЦА МЕТОК.\n {notification_text}.")
        
    elif action == "post_remove":
        removed_tags = [str(tag) for tag in Tag.objects.filter(pk__in=pk_set)]
        notification_text = (
            f"Удаление меток у вопроса №{instance.id} ({instance.text})\n"
            f"Метки: {', '.join(removed_tags)}\n"
            f"Результат IDS: Метки удалены"
        )
        ids.log_event(
            user=user.username if user != "unknown" else "unknown",
            ip=ip,
            action=notification_text,
            critical=True
        )
        logging.info(f"ТАБЛИЦА МЕТОК.\n {notification_text}.")

from alert_bot.notify import send_notification

ids = ids(alert_func=send_notification)


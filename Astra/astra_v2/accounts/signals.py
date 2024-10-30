# O:\Diplom\Astra\astra_v2\accounts\signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from ids_core import IDS

# Инициализация IDS
ids = IDS()

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    ids.log_event(user.username, "Вход в систему")
    ids.track_activity(user.username)

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    ids.log_event(user.username, "Выход из системы")

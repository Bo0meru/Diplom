# O:\Diplom\Astra\astra_v2\accounts\apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import accounts.signals  # Подключение сигналов

from django.contrib import messages
from django.contrib.auth.views import LoginView
from ids_core import IDS

class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)

# Инициализация IDS
ids = IDS()
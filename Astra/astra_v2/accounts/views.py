from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

from ids_core import IDS

# Инициализация IDS
ids = IDS()

class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        # Логируем неудачную попытку входа с помощью IDS
        ids.log_event(
            event_type="login_failed",
            username=self.request.POST.get('username', 'unknown'),
            ip_address=self.request.META.get('REMOTE_ADDR', 'unknown'),
            description="Неудачная попытка входа"
        )
        return super().form_invalid(form)

def login_register_view(request):
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()
    active_form = 'login'  # Форма по умолчанию

    if request.method == "POST":
        # Обработка авторизации
        if 'login' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    ids.log_event(
                        user=username,
                        action="Успешный вход",
                        critical=False
                    )
                    return redirect('/accounts/profile/')
                else:
                    ids.log_event(
                        user=username if username else "Неизвестный пользователь",
                        action="Неудачная попытка входа",
                        critical=True
                    )
                    messages.error(request, "Неверное имя пользователя или пароль.")
            else:
                messages.error(request, "Ошибка при авторизации. Проверьте данные.")

        # Обработка регистрации
        elif 'register' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                ids.log_event(
                    user=user.username,
                    action="Успешная регистрация",
                    critical=False
                )
                return redirect('/accounts/profile/')
            else:
                ids.log_event(
                    user="Неизвестный пользователь",
                    action="Ошибка регистрации",
                    critical=True
                )
                print("Ошибки формы регистрации:", register_form.errors)
                messages.error(request, "Ошибка при регистрации.")
                active_form = 'register'  # Переключаем активную форму на регистрацию

    return render(request, 'accounts/login.html', {
        'login_form': login_form,
        'register_form': register_form,
        'active_form': active_form,  # Передаём активную форму в шаблон
    })

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

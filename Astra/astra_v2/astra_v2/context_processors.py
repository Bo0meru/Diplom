from django.contrib.auth.models import Group

def check_user_access(request):
    """
    Проверяет, имеет ли пользователь доступ к разделу "служебное".
    """
    if request.user.is_authenticated:
        # Проверка на суперадминистратора
        if request.user.is_superuser:
            return {'has_service_access': True}

        # Проверка на принадлежность к группам
        allowed_groups = ['Методист', 'Администратор']
        user_groups = request.user.groups.values_list('name', flat=True)
        has_access = any(group in allowed_groups for group in user_groups)
        return {'has_service_access': has_access}

    # Если пользователь не аутентифицирован, доступ закрыт
    return {'has_service_access': False}
# PostgreSQL 
# Passwd: 4erevi4ki
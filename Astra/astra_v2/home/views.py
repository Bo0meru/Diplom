from django.shortcuts import render

def home(request):
    return render(request, 'home/home.html', {'debug_message': 'Шаблон рендерится'})

def about(request):
    return render(request, 'home/about.html')

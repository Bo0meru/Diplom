from django.shortcuts import render
import requests

def home(request):
    return render(request, 'home/home.html', {'debug_message': 'Шаблон рендерится'})

def about(request):
    return render(request, 'home/about.html')

def block_ip(ip):
    requests.post('http://127.0.0.1:5000/block_ip', json={'ip': ip, 'duration': 5})

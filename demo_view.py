from django.shortcuts import render
from django.http import HttpResponse

def demo_home(request):
    """Demo view to show stunning animations without URL issues"""
    with open('templates/home_demo.html', 'r') as f:
        content = f.read()
    return HttpResponse(content)
from django.shortcuts import render


def index(request):
    return render(request, 'taskstack_core/index.html')

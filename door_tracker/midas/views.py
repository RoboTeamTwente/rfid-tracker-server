from django.shortcuts import render


def dashboard(request):
    return render(request, 'midas/index.html')

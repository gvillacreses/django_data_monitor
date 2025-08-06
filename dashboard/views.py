from django.shortcuts import render

import requests
from django.conf import settings

def index(request):
    # return HttpResponse("¡Bienvenido a la aplicación Django!")
    data = {
        'title': "Landing Page' Dashboard",
    }
    return render(request, 'dashboard/index.html', data)

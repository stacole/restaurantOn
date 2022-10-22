from multiprocessing import context
from django.shortcuts import render
from django.http import HttpResponse

from vendor.models import Vendor

def home(request):
    # [:4] es para solo m ostrar 4 restaurantes en linea al inicio
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:4] # mostrar restaurantes al inicio si son aprovados.
    #print(vendors)  imprime los restaurantes en la consola
    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)
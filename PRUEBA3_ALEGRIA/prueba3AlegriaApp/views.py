from django.shortcuts import render, redirect, get_object_or_404
from 


# Create your views here.
def index(request):
    data = {
        'titulo' : 'Pagina de Inicio'
    }
    return render(request, 'index.html', data)
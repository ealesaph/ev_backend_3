from django.shortcuts import render


# Create your views here.
def index(request):
    data = {
        'titulo' : 'Pagina de Inicio'
    }
    return render(request, 'index.html', data)
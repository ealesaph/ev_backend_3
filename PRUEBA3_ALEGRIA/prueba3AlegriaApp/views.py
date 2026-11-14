from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Producto as Prod
from .forms import FormularioProducto as FormProd

# Create your views here.

def es_administrador(usuario):
    return usuario.is_staff

@login_required
def index(request):
    data = {
        'titulo' : 'Pagina de Inicio'
    }
    return render(request, 'index.html', data)

@login_required
def listar_productos(request):
    productos = Prod.objects.all()
    datos = {
        'titulo':'Listado de Productos',
        'productos':productos
    }
    return render(request, 'listar_productos.html', datos)

@login_required
def buscar_producto(request):
    nombre_buscado = request.GET.get('nombre', '')
    productos = Prod.objects.filter(nombre__icontains=nombre_buscado)
    datos = {
        'titulo':'Buscar Producto',
        'productos': productos,
        'nombre_buscado': nombre_buscado
    }
    return render(request, 'buscar_productos.html', datos)

@login_required
@user_passes_test(es_administrador)
def agregar_producto(request):
    if request.method == 'POST':
        formulario = FormProd(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('listar')
    else:
        formulario = FormProd()
    datos = {
            'titulo':'Agregar Producto',
            'formulario':formulario
        }
    return render(request, 'agregar_producto.html', datos)

@login_required
@user_passes_test(es_administrador)
def modificar_producto(request, id):
    producto = get_object_or_404(Prod, id=id)
    if request.method == 'POST':
        formulario = FormProd(request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            return redirect('listar')
    else:
        formulario = FormProd(instance=producto)
    datos = {
        'titulo':'Modificar Producto',
        'formulario':formulario,
        'producto':producto
    }
    return render(request, 'modificar_producto.html', datos)

@login_required
@user_passes_test(es_administrador)
def eliminar_producto(request, id):
    producto = get_object_or_404(Prod, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('listar')
    datos = {
        'titulo':'Eliminar Producto',
        'producto':producto
    }
    return render(request, 'eliminar_producto.html', datos)
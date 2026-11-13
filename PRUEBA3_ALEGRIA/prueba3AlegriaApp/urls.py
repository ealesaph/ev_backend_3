from django.urls import path
from django.contrib.auth import views as auth_views

from . import views as vw

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', vw.index, name='index'),
    path('listar/', vw.listar_productos, name='listar' ),
    path('buscar/', vw.buscar_producto, name='buscar'),
    path('agregar/', vw.agregar_producto, name='agregar'),
    path('modificar/<int:id>', vw.modificar_producto, name='modificar'),
    path('eliminar/<int:id>', vw.eliminar_producto, name='eliminar'),

]
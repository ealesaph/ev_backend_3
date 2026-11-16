from io import BytesIO
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .forms import FormularioProducto
from .models import Producto


class CargaImagenProductoTests(TestCase):
    def setUp(self):
        self.directorio_media = tempfile.TemporaryDirectory()
        self.addCleanup(self.directorio_media.cleanup)
        configuracion_media = override_settings(MEDIA_ROOT=self.directorio_media.name)
        configuracion_media.enable()
        self.addCleanup(configuracion_media.disable)

        usuario = get_user_model()
        self.administrador = usuario.objects.create_user(
            username='administrador',
            password='clave-segura-123',
            is_staff=True
        )
        self.client.force_login(self.administrador)

    def imagen_png(self, nombre='producto.png'):
        archivo = BytesIO()
        Image.new('RGB', (1, 1), color='red').save(archivo, format='PNG')
        return SimpleUploadedFile(nombre, archivo.getvalue(), content_type='image/png')

    def datos_producto(self):
        return {
            'nombre': 'Balón de fútbol',
            'descripcion': 'Balón de prueba',
            'stock': 5,
            'precio_unitario': 12000,
            'fecha_ingreso_dia': '16',
            'fecha_ingreso_mes': '11',
            'fecha_ingreso_anio': '2026',
            'categoria': 'Fútbol',
        }

    def test_agregar_producto_guarda_y_muestra_imagen(self):
        datos = self.datos_producto()
        datos['imagen'] = self.imagen_png()

        respuesta = self.client.post(reverse('agregar'), data=datos)

        self.assertRedirects(respuesta, reverse('listar'))
        producto = Producto.objects.get(nombre='Balón de fútbol')
        self.assertTrue(producto.imagen.name.startswith('productos/'))
        self.assertTrue(producto.imagen.storage.exists(producto.imagen.name))

        respuesta_listado = self.client.get(reverse('listar'))
        self.assertContains(respuesta_listado, producto.imagen.url)

    def test_modificar_producto_acepta_reemplazo_de_imagen(self):
        producto = Producto.objects.create(
            nombre='Balón de fútbol',
            descripcion='Balón de prueba',
            stock=5,
            precio_unitario=12000,
            fecha_ingreso='2026-11-16',
            categoria='Fútbol'
        )
        datos = self.datos_producto()
        datos['imagen'] = self.imagen_png('balon-nuevo.png')

        respuesta = self.client.post(
            reverse('modificar', args=[producto.id]),
            data=datos
        )

        self.assertRedirects(respuesta, reverse('listar'))
        producto.refresh_from_db()
        self.assertTrue(producto.imagen.name.endswith('balon-nuevo.png'))

    def test_borrar_imagen_no_modifica_descripcion(self):
        descripcion = 'Descripción que debe conservarse al borrar la imagen.'
        producto = Producto.objects.create(
            nombre='Producto con imagen',
            descripcion=descripcion,
            stock=5,
            precio_unitario=12000,
            fecha_ingreso='2026-11-16',
            categoria='Fútbol',
            imagen=self.imagen_png('imagen-a-borrar.png')
        )
        datos = self.datos_producto()
        datos['nombre'] = producto.nombre
        datos['descripcion'] = descripcion
        datos['imagen-clear'] = 'on'

        respuesta = self.client.post(
            reverse('modificar', args=[producto.id]),
            data=datos
        )

        self.assertRedirects(respuesta, reverse('listar'))
        producto.refresh_from_db()
        self.assertFalse(producto.imagen)
        self.assertEqual(producto.descripcion, descripcion)

    def test_listado_usuario_general_muestra_productos_en_tarjetas(self):
        Producto.objects.create(
            nombre='Balón de fútbol',
            descripcion='Balón de prueba',
            stock=5,
            precio_unitario=12000,
            fecha_ingreso='2026-11-16',
            categoria='Fútbol'
        )
        usuario_general = get_user_model().objects.create_user(
            username='cliente',
            password='clave-segura-123'
        )
        self.client.force_login(usuario_general)

        respuesta = self.client.get(reverse('listar'))

        self.assertContains(respuesta, 'class="card h-100 shadow-sm"')
        self.assertContains(respuesta, 'Balón de fútbol')
        self.assertContains(respuesta, 'Disponible')
        self.assertNotContains(respuesta, '<table')

    def test_listado_administrador_conserva_la_tabla(self):
        Producto.objects.create(
            nombre='Balón de fútbol',
            descripcion='Balón de prueba',
            stock=5,
            precio_unitario=12000,
            fecha_ingreso='2026-11-16',
            categoria='Fútbol'
        )

        respuesta = self.client.get(reverse('listar'))

        self.assertContains(respuesta, '<table class="table table-striped table-hover align-middle mb-0">')
        self.assertContains(respuesta, 'Acciones')
        self.assertNotContains(respuesta, 'class="card h-100 shadow-sm"')

    def test_fecha_usa_selects_separados_y_hoy_como_default(self):
        formulario = FormularioProducto()
        html = str(formulario['fecha_ingreso'])
        hoy = timezone.localdate()

        self.assertIn('class="row g-2"', html)
        self.assertIn('class="col-4"', html)
        self.assertIn('name="fecha_ingreso_dia"', html)
        self.assertIn('name="fecha_ingreso_mes"', html)
        self.assertIn('name="fecha_ingreso_anio"', html)
        self.assertLess(
            html.index('name="fecha_ingreso_dia"'),
            html.index('name="fecha_ingreso_mes"')
        )
        self.assertLess(
            html.index('name="fecha_ingreso_mes"'),
            html.index('name="fecha_ingreso_anio"')
        )
        self.assertIn('max="31"', html)
        self.assertIn('max="12"', html)
        self.assertIn('max="9999"', html)
        self.assertIn(f'value="{hoy.day}"', html)
        self.assertIn(f'value="{hoy.month}"', html)
        self.assertIn(f'value="{hoy.year}"', html)

    def test_fecha_invalida_o_fuera_de_rango_es_rechazada(self):
        datos = self.datos_producto()
        datos['fecha_ingreso_dia'] = '31'
        datos['fecha_ingreso_mes'] = '2'
        formulario = FormularioProducto(data=datos)

        self.assertFalse(formulario.is_valid())
        self.assertIn('fecha_ingreso', formulario.errors)

    def test_formulario_sugiere_categorias_existentes(self):
        Producto.objects.create(
            nombre='Balón de fútbol',
            descripcion='Balón de prueba',
            stock=5,
            precio_unitario=12000,
            fecha_ingreso=timezone.localdate(),
            categoria='Fútbol'
        )

        respuesta = self.client.get(reverse('agregar'))
        contenido = respuesta.content.decode()

        indice_campo = contenido.index('name="categoria"')
        indice_lista = contenido.index('id="categorias-autocompletar"')
        indice_opcion = contenido.index('data-categoria-sugerida="Fútbol"')
        self.assertGreater(indice_lista, indice_campo)
        self.assertGreater(indice_opcion, indice_lista)
        self.assertContains(respuesta, 'role="combobox"')
        self.assertContains(respuesta, 'role="listbox"')

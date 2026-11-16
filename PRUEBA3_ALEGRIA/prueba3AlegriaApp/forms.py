from datetime import date

from .models import Producto
from django import forms
from django.utils import timezone


class FechaSeparadaWidget(forms.MultiWidget):
    template_name = 'prueba3AlegriaApp/widgets/fecha_separada.html'

    def __init__(self, attrs=None):
        widgets = {
            'dia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 31,
                'placeholder': 'DD',
                'aria-label': 'Día',
            }),
            'mes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 12,
                'placeholder': 'MM',
                'aria-label': 'Mes',
            }),
            'anio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 9999,
                'placeholder': 'AAAA',
                'aria-label': 'Año',
            }),
        }
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]

    def id_for_label(self, id_):
        return f'{id_}_0'


class FechaSeparadaField(forms.MultiValueField):
    def __init__(self, **kwargs):
        fields = (
            forms.IntegerField(
                min_value=1,
                max_value=31,
                error_messages={
                    'min_value': 'El día debe estar entre 1 y 31.',
                    'max_value': 'El día debe estar entre 1 y 31.',
                    'invalid': 'Ingresa un día válido.',
                }
            ),
            forms.IntegerField(
                min_value=1,
                max_value=12,
                error_messages={
                    'min_value': 'El mes debe estar entre 1 y 12.',
                    'max_value': 'El mes debe estar entre 1 y 12.',
                    'invalid': 'Ingresa un mes válido.',
                }
            ),
            forms.IntegerField(
                min_value=1,
                max_value=9999,
                error_messages={
                    'min_value': 'Ingresa un año válido.',
                    'max_value': 'Ingresa un año válido.',
                    'invalid': 'Ingresa un año válido.',
                }
            ),
        )
        super().__init__(
            fields,
            widget=FechaSeparadaWidget(),
            error_messages={'incomplete': 'Completa día, mes y año.'},
            **kwargs
        )

    def compress(self, data_list):
        if data_list:
            dia, mes, anio = data_list
            try:
                return date(anio, mes, dia)
            except ValueError as error:
                raise forms.ValidationError(
                    'La fecha ingresada no existe.',
                    code='invalid'
                ) from error
        return None


class FormularioProducto(forms.ModelForm):
    fecha_ingreso = FechaSeparadaField(initial=timezone.localdate)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        anio_actual = timezone.localdate().year
        anios = set(range(anio_actual - 50, anio_actual + 11))
        if self.instance.fecha_ingreso:
            anios.add(self.instance.fecha_ingreso.year)
        self.fields['fecha_ingreso'].widget.years = sorted(anios)
        self.fields['categoria'].help_text = (
            'Escribe para filtrar categorías o ingresa una nueva.'
        )
        self.categorias_existentes = list(
            Producto.objects.values_list('categoria', flat=True)
            .distinct()
            .order_by('categoria')
        )

    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
            'precio_unitario': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'role': 'combobox',
                'aria-autocomplete': 'list',
                'aria-controls': 'categorias-autocompletar',
                'aria-expanded': 'false',
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
from datetime import date

from django import forms
from django.utils import timezone

from .models import Producto


class FechaIngresoWidget(forms.MultiWidget):
    template_name = 'widgets/fecha_ingreso.html'

    def __init__(self, attrs=None):
        widgets = [
            forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '31',
                'placeholder': 'Día',
                'inputmode': 'numeric',
            }),
            forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '12',
                'placeholder': 'Mes',
                'inputmode': 'numeric',
            }),
            forms.NumberInput(attrs={
                'class': 'form-control',
                'min': timezone.localdate().year - 5,
                'max': timezone.localdate().year + 100,
                'placeholder': 'Año',
                'inputmode': 'numeric',
            }),
        ]
        super().__init__(widgets, attrs)
        self.widgets_names = ['_dia', '_mes', '_anio']

    def decompress(self, value):
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]


class FechaIngresoField(forms.MultiValueField):
    def __init__(self, **kwargs):
        fields = [
            forms.IntegerField(min_value=1, max_value=31),
            forms.IntegerField(min_value=1, max_value=12),
            forms.IntegerField(min_value=timezone.localdate().year - 5, max_value=timezone.localdate().year + 100),
        ]
        super().__init__(
            fields,
            widget=FechaIngresoWidget(),
            initial=timezone.localdate,
            **kwargs
        )

    def compress(self, data_list):
        if not data_list:
            return None
        day, month, year = data_list
        try:
            return date(year, month, day)
        except ValueError as error:
            raise forms.ValidationError('Ingrese una fecha válida.') from error


class FormularioProducto(forms.ModelForm):
    fecha_ingreso = FechaIngresoField()

    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
            'precio_unitario': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
            'categoria': forms.TextInput(attrs={'class':'form-control'}),
        }
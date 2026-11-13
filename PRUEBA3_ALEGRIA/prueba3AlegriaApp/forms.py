from .models import Producto
from django import forms

class FormularioProducto(forms.ModelForm):
    fecha_ingreso = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(
            format='%d-%m-%Y',
            attrs={
                'class': 'form-control',
                'placeholder': 'dd-mm-aaaa'
            }
        )
    )
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
            'precio_unitario': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
            'categoria': forms.TextInput(attrs={'class':'form-control'}),
        }
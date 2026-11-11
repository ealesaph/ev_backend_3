from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(max_length= 255, null=False)
    descripcion = models.CharField(max_length=255)
    stock = models.IntegerField(
        default=0, null=False,
        validators= [
            MinValueValidator(0)
        ]
    )
    precio_unitario = models.IntegerField(
        validators = [
            MinValueValidator(0)
        ]
    )
    fecha_ingreso = models.DateField()
    categoria = models.CharField(max_length=255)
from django import forms
from .models import Producto, Ingrediente

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'descripcion', 'ingredientes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredientes'].required = False


class IngredienteForm(forms.ModelForm):
    """Formulario para crear y editar ingredientes (RF-15).

    Campos: nombre, unidad_medida, stock.
    Validaciones:
      - nombre: único (case-insensitive), no puede repetirse en BD.
      - stock: debe ser >= 0, no se permiten valores negativos.
    """
    class Meta:
        model = Ingrediente
        fields = ['nombre', 'unidad_medida', 'stock']
        labels = {
            'nombre': 'Nombre del ingrediente',
            'unidad_medida': 'Unidad de medida',
            'stock': 'Cantidad en inventario',
        }

    def clean_nombre(self):
        """Valida que el nombre sea único sin distinguir mayúsculas/minúsculas.
        Al editar, excluye el registro actual para no comparar consigo mismo.
        """
        nombre = self.cleaned_data['nombre']
        qs = Ingrediente.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un ingrediente con ese nombre.')
        return nombre

    def clean_stock(self):
        """Valida que la cantidad en inventario no sea negativa."""
        stock = self.cleaned_data['stock']
        if stock < 0:
            raise forms.ValidationError('La cantidad no puede ser negativa.')
        return stock
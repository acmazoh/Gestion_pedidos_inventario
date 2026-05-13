from django.contrib import admin
from .models import Producto, Categoria, Ingrediente, ProductoIngrediente


class ProductoIngredienteInline(admin.TabularInline):
    model = ProductoIngrediente
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    inlines = [ProductoIngredienteInline]
    list_display = ('nombre', 'categoria', 'precio', 'disponible')


admin.site.register(Categoria)


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock')

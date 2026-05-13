import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restin.settings')
django.setup()

from products.models import Producto

# Obtener lista de archivos en media/productos
media_path = Path('media/productos')
image_files = {f.stem.lower(): f.name for f in media_path.glob('*') if f.is_file()}

print(f"Imágenes encontradas: {len(image_files)}")
print("=" * 60)

# Mapeo manual de productos a imágenes (para casos especiales)
mapeo_manual = {
    'hamburguesa sencilla': 'Hamburguesa_Sencilla.jpeg',
    'hamburguesa doble': 'Hamburguesa_doble.jpeg',
    'hamburguesa bbq': 'Hamburguesa_BBQ.jpeg',
    'hamburguesa pollo crispy': 'Hamburguesa_pollo_crispy.jpeg',
    'perro sencillo': 'Perro_sencillo.jpeg',
    'perro especial': 'Perro_Especial.jpeg',
    'perro ranchero': 'perro_ranchero.jpeg',
    'papas francesas': 'papas_francesas.jpeg',
    'papas con queso y tocineta': 'papas_queso_tocineta.jpeg',
    'papas con carne desmechada': 'papas_carne_tocineta.jpeg',
    'papas mixtas': 'papas_mixtas.jpeg',
    'salchipapas': 'salchipapas.jpeg',
    'wrap de pollo': 'wrap_pollo.jpeg',
    'burrito mixto': 'burrito_mixto.jpeg',
    'nuggets de pollo': 'nuggets.jpeg',
    'alitas bbq  x 6': 'Alitas_BBQ_X6.jpeg',
    'alitas bbq  x 12': 'Alitas_BBQ_X12.jpeg',
    'alitas picantes x 6': 'Alitas_picantes_X6.jpeg',
    'alitas picantes x 12': 'Alitas_picantes_X12.jpeg',
    'coca cola': 'Coca_Cola.jpeg',
    'pepsi': 'pepsi.jpeg',
    'sprite': 'sprite.jpeg',
    'quatro': 'Quatro.jpeg',
    'jugo de mora': 'Jugo_mora.jpeg',
    'jugo de mango': 'Jugo_mango.jpeg',
    'jugo de fresa': 'Jugo_fresa.jpeg',
    'jugo de maracuya': 'Jugo_maracuya.jpeg',
    'malteada de chocolate': 'Malteada_chocolate.jpeg',
    'malteada de fresa': 'Malteada_fresa.jpeg',
    'malteada de vainilla': 'Malteada_vainilla.jpeg',
    'malteada de oreo': 'Malteada_oreo.jpeg',
    'sandwich club': 'sandwich_club.jpeg',
    'sandwich bbq': 'sandwich_BBQ.jpeg',
    'browie con helado': 'Brownie_con_helado.jpeg',
    'cheescake': 'cheesecake.jpeg',
}

productos = Producto.objects.all()
actualizados = 0
no_encontrados = []

for producto in productos:
    nombre_lower = producto.nombre.lower()
    
    # Buscar en mapeo manual
    if nombre_lower in mapeo_manual:
        archivo = mapeo_manual[nombre_lower]
        producto.imagen = f'productos/{archivo}'
        producto.save()
        print(f"✓ {producto.nombre:40} → {archivo}")
        actualizados += 1
    else:
        no_encontrados.append(producto.nombre)
        print(f"✗ {producto.nombre:40} → (no encontrada)")

print("=" * 60)
print(f"\nActualizados: {actualizados}/{len(productos)}")
if no_encontrados:
    print(f"\nProductos sin imagen ({len(no_encontrados)}):")
    for nombre in no_encontrados:
        print(f"  - {nombre}")

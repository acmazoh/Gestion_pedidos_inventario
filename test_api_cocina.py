#!/usr/bin/env python3
"""
Script de prueba para la API de Pedidos Activos en Tiempo Real.

Uso:
    python test_api_cocina.py

Este script te ayuda a verificar que la API está funcionando correctamente.
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/ventas/api/pedidos/activos/"
LOGIN_URL = f"{BASE_URL}/accounts/login/"

# Credenciales de prueba (cámbia según tu usuario)
USERNAME = "testuser"
PASSWORD = "testpass123"

def test_api():
    """Prueba la API de pedidos activos."""
    
    print("=" * 60)
    print("🧪 PRUEBA DE API - PEDIDOS ACTIVOS EN TIEMPO REAL")
    print("=" * 60)
    
    # Crear una sesión para mantener cookies
    session = requests.Session()
    
    # Paso 1: Login
    print("\n1️⃣  Intentando login...")
    try:
        # Primero, obtener el token CSRF
        login_page = session.get(LOGIN_URL)
        csrf_token = None
        
        # Buscar el token CSRF en la página
        import re
        match = re.search(r'csrfmiddlewaretoken["\']?\s*value="([^"]+)"', login_page.text)
        if match:
            csrf_token = match.group(1)
        
        # Login
        login_data = {
            'username': USERNAME,
            'password': PASSWORD,
            'csrfmiddlewaretoken': csrf_token or '',
        }
        
        response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        
        if response.status_code == 200 and 'pedidos' in response.url:
            print("   ✅ Login exitoso")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            print("   💡 Tip: Verifica las credenciales")
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        print("   💡 Tip: Asegúrate de que el servidor está corriendo")
        return
    
    # Paso 2: Probar API
    print("\n2️⃣  Consultando API de pedidos activos...")
    try:
        response = session.get(API_ENDPOINT)
        
        if response.status_code == 200:
            print("   ✅ API respondió correctamente (200 OK)")
            
            data = response.json()
            
            print("\n📊 Respuesta JSON:")
            print("-" * 60)
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("-" * 60)
            
            # Información adicional
            print("\n📈 Estadísticas:")
            print(f"   Total de pedidos: {data['total']}")
            print(f"   Timestamp: {data['timestamp']}")
            print(f"   Pedidos en cocina: {len(data['pedidos'])}")
            
            if data['pedidos']:
                print("\n📋 Detalles de pedidos:")
                for idx, pedido in enumerate(data['pedidos'], 1):
                    nuevo = "🆕 NUEVO" if pedido['es_nuevo'] else ""
                    print(f"\n   Pedido #{pedido['id']} - {pedido['mesa_o_online']} {nuevo}")
                    print(f"   Estado: {pedido['estado']}")
                    print(f"   Hora: {pedido['hora_formateada']}")
                    print(f"   Productos: {pedido['total_items']}")
                    for item in pedido['items']:
                        print(f"      • {item['cantidad']}x {item['producto']}")
            else:
                print("\n   ℹ️  No hay pedidos activos en este momento")
                print("   💡 Tip: Crea una nueva orden desde el panel de mesero")
            
        elif response.status_code == 401:
            print("   ❌ No autorizado (401)")
            print("   💡 Tip: El login falló o no está autenticado")
            
        else:
            print(f"   ❌ Error {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error en la solicitud: {e}")
        print("   💡 Tip: Verifica que el servidor esté corriendo en {BASE_URL}")
    
    # Paso 3: Prueba de actualización en tiempo real
    print("\n3️⃣  Monitoreando actualizaciones (5 segundos)...")
    print("   Presiona Ctrl+C para detener")
    print("-" * 60)
    
    try:
        last_total = 0
        for i in range(5):
            response = session.get(API_ENDPOINT)
            if response.status_code == 200:
                data = response.json()
                current_total = data['total']
                
                # Mostrar cambios
                if current_total != last_total:
                    print(f"   ⏱️  [{i+1}] Cambio detectado: {current_total} pedidos")
                    last_total = current_total
                else:
                    print(f"   ⏱️  [{i+1}] Sin cambios: {current_total} pedidos")
                
                if i < 4:
                    time.sleep(1)
    except KeyboardInterrupt:
        print("\n   ⏹️  Monitoreo detenido")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60)

def test_curl_commands():
    """Imprime comandos curl para probar manualmente."""
    
    print("\n" + "=" * 60)
    print("📝 COMANDOS CURL PARA PRUEBA MANUAL")
    print("=" * 60)
    
    print("""
1. OBTENER PEDIDOS ACTIVOS (requiere autenticación):

   curl -b cookies.txt \\
     -H "Accept: application/json" \\
     http://localhost:8000/ventas/api/pedidos/activos/

2. USAR CON JQ PARA FORMATO BONITO:

   curl -s -b cookies.txt \\
     http://localhost:8000/ventas/api/pedidos/activos/ | jq .

3. MONITOREAR EN TIEMPO REAL (Linux/Mac):

   watch -n 3 'curl -s -b cookies.txt \\
     http://localhost:8000/ventas/api/pedidos/activos/ | jq .total'

4. DESDE PYTHON:

   import requests
   response = requests.get('http://localhost:8000/ventas/api/pedidos/activos/')
   print(response.json())
    """)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--curl":
        test_curl_commands()
    else:
        print("\n💡 Tip: Ejecuta con --curl para ver comandos curl\n")
        test_api()

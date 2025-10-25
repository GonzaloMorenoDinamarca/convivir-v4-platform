"""
Script de Verificación de Versión - CONVIVIR v4.0
Verifica que tengas la versión correcta del archivo database.py
"""

import os

def verificar_version():
    print("="*70)
    print("VERIFICACIÓN DE VERSIÓN - CONVIVIR v4.0")
    print("="*70)
    print()
    
    # Verificar que database.py existe
    if not os.path.exists('database.py'):
        print("❌ ERROR: No se encuentra database.py")
        print("   Asegúrate de estar en el directorio correcto")
        return False
    
    # Leer el contenido
    with open('database.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar marcadores de versión
    print("Verificando marcadores de versión...")
    print()
    
    # Verificar que NO tenga las relaciones problemáticas
    if 'interacciones_origen = relationship("Interaccion"' in contenido:
        print("❌ VERSIÓN INCORRECTA DETECTADA")
        print("   Tu database.py tiene las relaciones problemáticas")
        print("   Versión detectada: v4.0.0 - v4.0.3 (con errores)")
        print()
        print("SOLUCIÓN:")
        print("   1. Descarga el ZIP más reciente")
        print("   2. Reemplaza database.py con el del ZIP")
        print("   3. Ejecuta este script nuevamente")
        return False
    
    # Verificar que tenga el comentario correcto
    if '# Relaciones eliminadas para evitar errores de SQLAlchemy' in contenido:
        print("✅ VERSIÓN CORRECTA DETECTADA")
        print("   Versión: v4.0.4 (Estable)")
        print()
        
        # Contar líneas
        lineas = contenido.count('\n')
        print(f"   Líneas de código: {lineas}")
        print()
        
        print("="*70)
        print("✅ TU VERSIÓN ES CORRECTA")
        print("="*70)
        print()
        print("Puedes ejecutar la aplicación con: python app.py")
        return True
    
    else:
        print("⚠️  VERSIÓN DESCONOCIDA")
        print("   No se pudo determinar la versión de database.py")
        print()
        print("SOLUCIÓN:")
        print("   Descarga el ZIP más reciente (v4.0.4) y reemplaza database.py")
        return False

if __name__ == "__main__":
    verificar_version()


#!/usr/bin/env python3
"""
Script de diagnóstico para CONVIVIR v4.0
Verifica que todos los componentes estén correctamente instalados
"""

import sys
import os

print("=" * 80)
print("🔍 CONVIVIR v4.0 - Diagnóstico del Sistema")
print("=" * 80)
print()

# 1. Verificar versión de Python
print("1️⃣ Verificando Python...")
print(f"   Versión: {sys.version}")
python_version = sys.version_info
if python_version.major == 3 and python_version.minor >= 8:
    print("   ✅ Versión de Python compatible")
else:
    print("   ⚠️  Se recomienda Python 3.8 o superior")
print()

# 2. Verificar dependencias
print("2️⃣ Verificando dependencias...")
dependencias = {
    'flask': 'Flask',
    'sqlalchemy': 'SQLAlchemy',
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'tensorflow': 'TensorFlow',
    'transformers': 'Transformers',
    'networkx': 'NetworkX',
    'plotly': 'Plotly',
    'psycopg2': 'psycopg2-binary'
}

faltantes = []
for modulo, nombre in dependencias.items():
    try:
        __import__(modulo)
        print(f"   ✅ {nombre}")
    except ImportError:
        print(f"   ❌ {nombre} - NO INSTALADO")
        faltantes.append(nombre)
print()

if faltantes:
    print("⚠️  DEPENDENCIAS FALTANTES:")
    print("   Ejecuta: pip install -r requirements.txt")
    print()

# 3. Verificar archivos clave
print("3️⃣ Verificando archivos del proyecto...")
archivos_clave = [
    'app.py',
    'database.py',
    'modelo_lstm.py',
    'modelo_nlp.py',
    'modelo_gnn.py',
    'start.py',
    'requirements.txt',
    'templates/index.html',
    'templates/configurar_cursos.html',
    'templates/gestionar_estudiantes.html',
    'templates/gestionar_cohortes.html',
    'templates/ingresar_datos.html',
    'templates/observaciones_estudiantes.html'
]

archivos_faltantes = []
for archivo in archivos_clave:
    if os.path.exists(archivo):
        print(f"   ✅ {archivo}")
    else:
        print(f"   ❌ {archivo} - NO ENCONTRADO")
        archivos_faltantes.append(archivo)
print()

if archivos_faltantes:
    print("⚠️  ARCHIVOS FALTANTES:")
    for archivo in archivos_faltantes:
        print(f"   - {archivo}")
    print()

# 4. Verificar base de datos
print("4️⃣ Verificando base de datos...")
if os.path.exists('convivir_v4.db'):
    size = os.path.getsize('convivir_v4.db') / (1024 * 1024)
    print(f"   ✅ convivir_v4.db ({size:.2f} MB)")
else:
    print("   ⚠️  convivir_v4.db no encontrada (se creará al iniciar)")
print()

# 5. Verificar rutas en app.py
print("5️⃣ Verificando rutas de la aplicación...")
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
        rutas_importantes = [
            "'/configurar_cursos'",
            "'/gestionar_estudiantes'",
            "'/gestionar_cohortes'",
            "'/ingresar_datos'",
            "'/observaciones_estudiantes'"
        ]
        for ruta in rutas_importantes:
            if ruta in contenido:
                print(f"   ✅ Ruta {ruta} definida")
            else:
                print(f"   ❌ Ruta {ruta} NO definida")
except Exception as e:
    print(f"   ❌ Error al leer app.py: {e}")
print()

# Resumen
print("=" * 80)
if not faltantes and not archivos_faltantes:
    print("✅ DIAGNÓSTICO COMPLETO")
    print()
    print("Todo está listo. Para iniciar la aplicación:")
    print("   python start.py")
    print()
    print("Luego accede a: http://localhost:5000")
else:
    print("⚠️  SE ENCONTRARON PROBLEMAS")
    print()
    if faltantes:
        print("Instala las dependencias faltantes:")
        print("   pip install -r requirements.txt")
        print()
    if archivos_faltantes:
        print("Verifica que hayas descomprimido correctamente el ZIP")
        print("y que estés en el directorio correcto.")
print("=" * 80)


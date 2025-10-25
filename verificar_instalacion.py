"""
Script de Verificación de Instalación - CONVIVIR v4.0
Verifica qué dependencias están instaladas y cuáles faltan
"""

import sys

print("=" * 70)
print("VERIFICACIÓN DE DEPENDENCIAS - CONVIVIR v4.0")
print("=" * 70)
print(f"Python: {sys.version}")
print("=" * 70)

modulos = {
    'flask': ('Framework Web', True),
    'pandas': ('Análisis de Datos', True),
    'numpy': ('Computación Numérica', True),
    'openpyxl': ('Lectura de Excel', True),
    'sklearn': ('Machine Learning Básico', True),
    'networkx': ('Análisis de Redes (GNN)', True),
    'sqlalchemy': ('Base de Datos', True),
    'plotly': ('Visualizaciones', True),
    'matplotlib': ('Gráficos', False),
    'tensorflow': ('Deep Learning (LSTM)', False),
    'transformers': ('NLP Avanzado con BETO', False)
}

instalados = []
faltantes_criticos = []
faltantes_opcionales = []

print("\nEstado de Módulos:\n")

for modulo, (descripcion, es_critico) in modulos.items():
    try:
        mod = __import__(modulo)
        version = getattr(mod, '__version__', 'N/A')
        print(f"✅ {modulo:20s} v{version:10s} - {descripcion}")
        instalados.append(modulo)
    except ImportError:
        simbolo = "❌" if es_critico else "⚠️ "
        print(f"{simbolo} {modulo:20s} {'FALTANTE':10s} - {descripcion}")
        if es_critico:
            faltantes_criticos.append(modulo)
        else:
            faltantes_opcionales.append(modulo)

print("\n" + "=" * 70)
print(f"Instalados: {len(instalados)}/{len(modulos)}")
print("=" * 70)

# Análisis de estado
if len(faltantes_criticos) == 0:
    print("\n✅ DEPENDENCIAS CRÍTICAS: TODAS INSTALADAS")
    print("   El sistema funcionará correctamente.")
else:
    print(f"\n❌ DEPENDENCIAS CRÍTICAS FALTANTES: {len(faltantes_criticos)}")
    print(f"   Instalar: pip install {' '.join(faltantes_criticos)}")

if len(faltantes_opcionales) > 0:
    print(f"\n⚠️  DEPENDENCIAS OPCIONALES FALTANTES: {len(faltantes_opcionales)}")
    for mod in faltantes_opcionales:
        if mod == 'tensorflow':
            print("   - tensorflow: Se usará modelo LSTM simplificado (promedio móvil)")
        elif mod == 'transformers':
            print("   - transformers: Se usará NLP basado en reglas (diccionarios)")
        else:
            print(f"   - {mod}: Funcionalidad reducida")
    print(f"\n   Para instalar (opcional): pip install {' '.join(faltantes_opcionales)}")

# Funcionalidades disponibles
print("\n" + "=" * 70)
print("FUNCIONALIDADES DISPONIBLES")
print("=" * 70)

funcionalidades = {
    'Base de Datos SQLite': ['sqlalchemy'],
    'Carga de Datos Excel': ['pandas', 'openpyxl'],
    'Análisis de Redes Sociales (GNN)': ['networkx'],
    'Dashboard y Visualizaciones': ['flask', 'plotly'],
    'Sistema de Alertas': ['sqlalchemy', 'pandas'],
    'Predicción LSTM (Completa)': ['tensorflow', 'numpy', 'sklearn'],
    'Predicción LSTM (Simplificada)': ['pandas', 'numpy'],
    'NLP Avanzado (Transformers)': ['transformers'],
    'NLP Básico (Reglas)': ['pandas']
}

for funcionalidad, deps in funcionalidades.items():
    todos_instalados = all(dep in instalados for dep in deps)
    if todos_instalados:
        print(f"✅ {funcionalidad}")
    else:
        # Verificar si hay versión simplificada
        if 'Completa' in funcionalidad:
            continue  # Ya se mostrará la versión simplificada
        elif 'Simplificada' in funcionalidad or 'Básico' in funcionalidad:
            deps_basicas = [d for d in deps if d not in ['tensorflow', 'transformers']]
            if all(dep in instalados for dep in deps_basicas):
                print(f"⚠️  {funcionalidad} (versión de respaldo)")
        else:
            print(f"❌ {funcionalidad} - Faltan: {', '.join([d for d in deps if d not in instalados])}")

# Recomendaciones
print("\n" + "=" * 70)
print("RECOMENDACIONES")
print("=" * 70)

if len(faltantes_criticos) > 0:
    print("\n🔴 ACCIÓN REQUERIDA:")
    print(f"   pip install {' '.join(faltantes_criticos)}")
elif len(faltantes_opcionales) == 0:
    print("\n🟢 INSTALACIÓN COMPLETA")
    print("   Todas las funcionalidades están disponibles.")
    print("   Ejecuta: python app.py")
else:
    print("\n🟡 INSTALACIÓN FUNCIONAL")
    print("   El sistema funcionará correctamente con funcionalidades básicas.")
    print("   Ejecuta: python app.py")
    if 'tensorflow' in faltantes_opcionales:
        print("\n   Para habilitar predicción LSTM completa:")
        print("   pip install tensorflow")
    if 'transformers' in faltantes_opcionales:
        print("\n   Para habilitar NLP avanzado:")
        print("   pip install transformers")

print("\n" + "=" * 70)


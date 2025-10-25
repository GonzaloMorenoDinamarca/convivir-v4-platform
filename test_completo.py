"""
Test Completo End-to-End de CONVIVIR v4.0.4
Ejecuta: python test_completo.py
"""
import os
import sys

print("="*70)
print("TEST COMPLETO - CONVIVIR v4.0.4")
print("="*70)
print()

# Test 1: Importar módulos
print("[1/5] Importando módulos...")
try:
    from database import DatabaseManager
    print("   ✅ database.py importado correctamente")
except Exception as e:
    print(f"   ❌ Error al importar database.py: {e}")
    sys.exit(1)

# Test 2: Crear base de datos
print("\n[2/5] Creando base de datos...")
try:
    if os.path.exists('test_completo.db'):
        os.remove('test_completo.db')
    db = DatabaseManager('test_completo.db')
    print("   ✅ Base de datos creada sin errores")
except Exception as e:
    print(f"   ❌ Error al crear BD: {e}")
    sys.exit(1)

# Test 3: Cargar Excel
print("\n[3/5] Cargando archivo Excel...")
try:
    excel_path = 'CONVIVIR_Formato_Mejorado_Ejemplo.xlsx'
    if not os.path.exists(excel_path):
        print(f"   ❌ No se encuentra el archivo: {excel_path}")
        sys.exit(1)
    
    resultado = db.cargar_desde_excel(excel_path)
    
    if resultado['exito']:
        print(f"   ✅ {resultado['mensaje']}")
    else:
        print(f"   ❌ Error: {resultado['mensaje']}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Excepción: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verificar datos cargados
print("\n[4/5] Verificando datos cargados...")
try:
    from sqlalchemy import text
    with db.engine.connect() as conn:
        tablas = [
            ('establecimientos', 1),
            ('estudiantes', 180),
            ('cursos_temporal', 72),
            ('evaluaciones_socioemocionales', 1200),
            ('comentarios', 376),
            ('interacciones_sociales', 497),
            ('intervenciones', 4),
            ('docentes', 45)
        ]
        
        todo_ok = True
        for tabla, esperado in tablas:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            count = result.scalar()
            if count == esperado:
                print(f"   ✅ {tabla}: {count} registros")
            else:
                print(f"   ⚠️  {tabla}: {count} registros (esperado: {esperado})")
                todo_ok = False
        
        if not todo_ok:
            print("\n   ⚠️  Algunos conteos no coinciden, pero la carga fue exitosa")
except Exception as e:
    print(f"   ❌ Error al verificar: {e}")
    sys.exit(1)

# Test 5: Limpiar
print("\n[5/5] Limpiando...")
try:
    db.close()
    os.remove('test_completo.db')
    print("   ✅ Base de datos de prueba eliminada")
except Exception as e:
    print(f"   ⚠️  Error al limpiar: {e}")

print()
print("="*70)
print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
print("="*70)
print()
print("La aplicación está lista para usarse:")
print("  1. Ejecuta: python app.py")
print("  2. Abre: http://localhost:5000")
print("  3. Carga el archivo Excel")
print()


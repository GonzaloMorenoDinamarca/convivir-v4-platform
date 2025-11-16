"""
Script de migración para implementar el sistema de cohortes
Convierte los cursos actuales en cohortes con seguimiento longitudinal
"""

import sqlite3
from datetime import datetime

def migrar_a_cohortes(db_path='convivir_v4.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Iniciando migración al sistema de cohortes...")
    
    # 1. Crear tablas nuevas
    print("\n📋 Paso 1: Creando tablas cohortes y cursos_anuales...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cohortes (
            cohorte_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cohorte TEXT NOT NULL,
            ano_ingreso INTEGER NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cursos_anuales (
            curso_anual_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cohorte_id INTEGER NOT NULL,
            ano_academico INTEGER NOT NULL,
            nombre_curso TEXT NOT NULL,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cohorte_id) REFERENCES cohortes(cohorte_id)
        )
    ''')
    
    # 2. Agregar columna cohorte_id a estudiantes si no existe
    print("\n📋 Paso 2: Agregando columna cohorte_id a estudiantes...")
    
    try:
        cursor.execute('ALTER TABLE estudiantes ADD COLUMN cohorte_id INTEGER')
        print("   ✅ Columna cohorte_id agregada")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("   ℹ️  Columna cohorte_id ya existe")
        else:
            raise
    
    # 3. Obtener cursos únicos actuales
    print("\n📋 Paso 3: Identificando cursos existentes...")
    
    cursor.execute('''
        SELECT DISTINCT curso_id FROM cursos_temporal
        ORDER BY curso_id
    ''')
    
    cursos_existentes = [row[0] for row in cursor.fetchall()]
    print(f"   Encontrados {len(cursos_existentes)} cursos: {', '.join(cursos_existentes)}")
    
    # 4. Crear cohortes y cursos anuales para cada curso existente
    print("\n📋 Paso 4: Creando cohortes para cursos existentes...")
    
    ano_actual = datetime.now().year
    
    for curso_id in cursos_existentes:
        # Crear cohorte
        nombre_cohorte = f"Cohorte {curso_id} ({ano_actual})"
        
        cursor.execute('''
            INSERT INTO cohortes (nombre_cohorte, ano_ingreso, activo)
            VALUES (?, ?, 1)
        ''', (nombre_cohorte, ano_actual))
        
        cohorte_id = cursor.lastrowid
        
        # Crear curso anual activo
        cursor.execute('''
            INSERT INTO cursos_anuales (cohorte_id, ano_academico, nombre_curso, activo)
            VALUES (?, ?, ?, 1)
        ''', (cohorte_id, ano_actual, curso_id))
        
        # Actualizar estudiantes de este curso
        cursor.execute('''
            UPDATE estudiantes
            SET cohorte_id = ?
            WHERE curso_id = ?
        ''', (cohorte_id, curso_id))
        
        estudiantes_actualizados = cursor.rowcount
        
        print(f"   ✅ Creada cohorte {cohorte_id}: '{nombre_cohorte}' ({estudiantes_actualizados} estudiantes)")
    
    # 5. Commit y cerrar
    conn.commit()
    
    # 6. Verificar resultados
    print("\n📊 Verificando migración...")
    
    cursor.execute('SELECT COUNT(*) FROM cohortes')
    total_cohortes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM cursos_anuales')
    total_cursos_anuales = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM estudiantes WHERE cohorte_id IS NOT NULL')
    estudiantes_con_cohorte = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM estudiantes')
    total_estudiantes = cursor.fetchone()[0]
    
    print(f"   📌 Total de cohortes creadas: {total_cohortes}")
    print(f"   📌 Total de cursos anuales: {total_cursos_anuales}")
    print(f"   📌 Estudiantes asignados a cohortes: {estudiantes_con_cohorte}/{total_estudiantes}")
    
    conn.close()
    
    print("\n✅ ¡Migración completada exitosamente!")
    print("\n💡 Ahora puedes usar las funciones de promoción de curso sin perder datos históricos.")

if __name__ == '__main__':
    migrar_a_cohortes()

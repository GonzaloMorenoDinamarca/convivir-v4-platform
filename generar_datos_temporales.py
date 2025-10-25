"""
Script para generar datos temporales adicionales para análisis LSTM
"""

import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('convivir_v4.db')
cursor = conn.cursor()

# Obtener cursos existentes
cursor.execute("SELECT DISTINCT curso_id FROM cursos_temporal")
cursos = [row[0] for row in cursor.fetchall()]

print(f"Generando datos temporales para {len(cursos)} cursos...")

# Obtener la fecha más reciente
cursor.execute("SELECT MAX(fecha_registro) FROM cursos_temporal")
ultima_fecha = cursor.fetchone()[0]

if ultima_fecha:
    ultima_fecha = datetime.fromisoformat(ultima_fecha)
else:
    ultima_fecha = datetime.now() - timedelta(weeks=20)

# Generar 15 semanas adicionales de datos para cada curso
for curso_id in cursos:
    # Obtener último registro del curso
    cursor.execute("""
        SELECT clima_escolar_promedio, nivel_empatia_promedio, nivel_resolucion_conflictos_promedio
        FROM cursos_temporal
        WHERE curso_id = ?
        ORDER BY fecha_registro DESC
        LIMIT 1
    """, (curso_id,))
    
    ultimo_registro = cursor.fetchone()
    if ultimo_registro:
        clima_base = ultimo_registro[0]
        empatia_base = ultimo_registro[1]
        conflictos_base = ultimo_registro[2]
    else:
        clima_base = 7.5
        empatia_base = 7.0
        conflictos_base = 6.5
    
    # Generar 15 semanas de datos
    for i in range(1, 16):
        fecha = ultima_fecha + timedelta(weeks=i)
        
        # Variación aleatoria con tendencia
        variacion = random.uniform(-0.3, 0.4)
        clima = max(1, min(10, clima_base + variacion + (i * 0.02)))  # Tendencia ligeramente positiva
        empatia = max(1, min(10, empatia_base + random.uniform(-0.2, 0.3) + (i * 0.015)))
        conflictos = max(1, min(10, conflictos_base + random.uniform(-0.2, 0.3) + (i * 0.01)))
        
        # Insertar registro
        cursor.execute("""
            INSERT INTO cursos_temporal (
                establecimiento_id, fecha_registro, periodo, curso_id,
                total_estudiantes, clima_escolar_promedio, apoyo_docentes_promedio,
                participacion_estudiantes_promedio, nivel_empatia_promedio,
                nivel_autoestima_promedio, nivel_resolucion_conflictos_promedio,
                incidentes_bullying, incidentes_violencia_fisica, incidentes_discriminacion,
                reportes_anonimos, asistencia_promedio_porcentaje, promedio_notas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'EST_001',
            fecha.isoformat(),
            f'Semana {i}',
            curso_id,
            30,
            round(clima, 2),
            round(random.uniform(7.0, 9.0), 2),
            round(random.uniform(6.5, 8.5), 2),
            round(empatia, 2),
            round(random.uniform(6.5, 8.5), 2),
            round(conflictos, 2),
            random.randint(0, 2),
            random.randint(0, 1),
            random.randint(0, 1),
            random.randint(0, 3),
            round(random.uniform(85, 95), 2),
            round(random.uniform(5.5, 6.8), 2)
        ))
    
    print(f"   ✅ Curso {curso_id}: 15 semanas adicionales generadas")

# Generar algunas alertas de ejemplo
print("\nGenerando alertas de ejemplo...")

alertas = [
    ('Riesgo Predictivo', 'alta', '1°A', 'EST_001_001', 'Predicción LSTM indica descenso en clima escolar', 'Realizar taller de convivencia'),
    ('Sentimiento Negativo', 'media', '2°B', 'EST_001_045', 'Comentarios con sentimiento negativo detectados', 'Entrevista con estudiante y apoderados'),
    ('Aislamiento Social', 'alta', '3°A', 'EST_001_089', 'Estudiante con pocas conexiones sociales', 'Actividad de integración grupal'),
    ('Descenso Rendimiento', 'media', '1°B', 'EST_001_025', 'Disminución en participación y notas', 'Apoyo académico personalizado'),
]

for tipo, prioridad, curso, estudiante, mensaje, recomendacion in alertas:
    cursor.execute("""
        INSERT INTO alertas (
            fecha_creacion, tipo_alerta, nivel_prioridad, curso_id,
            estudiante_id, mensaje, recomendacion, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        tipo,
        prioridad,
        curso,
        estudiante,
        mensaje,
        recomendacion,
        'pendiente'
    ))
    print(f"   ✅ Alerta: {tipo} - {prioridad}")

conn.commit()
conn.close()

print("\n✅ Datos temporales y alertas generados exitosamente")
print(f"   Total de registros temporales: {len(cursos) * 15}")
print(f"   Total de alertas: {len(alertas)}")


"""
Generador de Datos Científicamente Realistas para Validación de Modelo LSTM
Basado en literatura científica sobre convivencia escolar
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

# Parámetros basados en literatura científica
np.random.seed(42)  # Reproducibilidad

class GeneradorDatosCientificos:
    """
    Genera datos sintéticos pero realistas basados en:
    - Patrones estacionales (inicio/fin de año escolar)
    - Tendencias de mejora/deterioro
    - Correlaciones entre variables
    - Eventos disruptivos (crisis, intervenciones)
    """
    
    def __init__(self, n_semanas=60, n_cursos=6):
        self.n_semanas = n_semanas
        self.n_cursos = n_cursos
        self.fecha_inicio = datetime.now() - timedelta(weeks=n_semanas)
        
    def generar_patron_estacional(self, semana):
        """
        Patrón estacional basado en ciclo escolar chileno
        - Inicio año (marzo): Valores altos (motivación)
        - Medio año (junio-julio): Descenso (fatiga)
        - Fin año (noviembre-diciembre): Descenso mayor (estrés)
        """
        # Convertir semana a mes del año escolar (marzo=0, diciembre=9)
        mes_escolar = (semana % 40) / 4  # 40 semanas = año escolar
        
        # Patrón sinusoidal con descenso hacia fin de año
        estacional = 1.0 - 0.3 * np.sin(mes_escolar * np.pi / 5)
        return estacional
    
    def generar_tendencia_curso(self, curso_tipo):
        """
        Genera tendencia específica por tipo de curso
        - Tipo A: Mejora sostenida (intervenciones efectivas)
        - Tipo B: Estable (sin intervenciones)
        - Tipo C: Deterioro gradual (problemas no atendidos)
        """
        if curso_tipo == 'A':
            return 0.015  # Mejora de 0.015 puntos por semana
        elif curso_tipo == 'B':
            return 0.0    # Estable
        else:
            return -0.01  # Deterioro de 0.01 puntos por semana
    
    def generar_evento_disruptivo(self, semana, tipo='crisis'):
        """
        Eventos disruptivos que afectan la convivencia
        - Crisis: Descenso abrupto
        - Intervención: Mejora gradual posterior
        """
        if tipo == 'crisis':
            return -1.5  # Descenso de 1.5 puntos
        elif tipo == 'intervencion':
            return 0.8   # Mejora de 0.8 puntos
        return 0.0
    
    def generar_serie_temporal_curso(self, curso_id, tipo_curso, eventos=[]):
        """
        Genera serie temporal realista para un curso
        
        Args:
            curso_id: Identificador del curso
            tipo_curso: 'A', 'B', o 'C'
            eventos: Lista de (semana, tipo_evento)
        
        Returns:
            DataFrame con serie temporal
        """
        datos = []
        
        # Valores base (ligeramente diferentes por curso)
        base_clima = np.random.uniform(7.0, 8.0)
        base_empatia = np.random.uniform(6.5, 7.5)
        base_conflictos = np.random.uniform(6.0, 7.0)
        
        # Tendencia del curso
        tendencia = self.generar_tendencia_curso(tipo_curso)
        
        # Generar cada semana
        for semana in range(self.n_semanas):
            fecha = self.fecha_inicio + timedelta(weeks=semana)
            
            # Componente estacional
            factor_estacional = self.generar_patron_estacional(semana)
            
            # Componente de tendencia
            efecto_tendencia = tendencia * semana
            
            # Componente de eventos
            efecto_eventos = 0.0
            for evento_semana, tipo_evento in eventos:
                if semana == evento_semana:
                    efecto_eventos = self.generar_evento_disruptivo(semana, tipo_evento)
                elif semana > evento_semana and tipo_evento == 'intervencion':
                    # Efecto residual de intervención (decae exponencialmente)
                    semanas_desde = semana - evento_semana
                    efecto_eventos += 0.8 * np.exp(-semanas_desde / 10)
            
            # Ruido aleatorio (variabilidad semanal)
            ruido = np.random.normal(0, 0.3)
            
            # Calcular valores finales
            clima = base_clima * factor_estacional + efecto_tendencia + efecto_eventos + ruido
            empatia = base_empatia * factor_estacional + efecto_tendencia * 0.8 + efecto_eventos * 0.7 + ruido * 0.8
            conflictos = base_conflictos * factor_estacional + efecto_tendencia * 0.6 + efecto_eventos * 0.5 + ruido * 0.7
            
            # Correlaciones entre variables (clima afecta empatía y conflictos)
            empatia += (clima - 7.0) * 0.3
            conflictos += (clima - 7.0) * 0.25
            
            # Limitar a escala 1-10
            clima = np.clip(clima, 1.0, 10.0)
            empatia = np.clip(empatia, 1.0, 10.0)
            conflictos = np.clip(conflictos, 1.0, 10.0)
            
            # Otras variables correlacionadas
            apoyo_docentes = np.clip(clima + np.random.normal(0.5, 0.3), 1.0, 10.0)
            participacion = np.clip(empatia + np.random.normal(0.3, 0.4), 1.0, 10.0)
            autoestima = np.clip(empatia + np.random.normal(0.2, 0.3), 1.0, 10.0)
            
            # Incidentes (inversamente correlacionados con clima)
            prob_bullying = max(0, (10 - clima) / 10)
            incidentes_bullying = np.random.poisson(prob_bullying * 2)
            incidentes_violencia = np.random.poisson(prob_bullying * 0.5)
            incidentes_discriminacion = np.random.poisson(prob_bullying * 0.3)
            reportes_anonimos = np.random.poisson(prob_bullying * 1.5)
            
            # Asistencia y notas (correlacionadas con clima)
            asistencia = np.clip(85 + (clima - 7) * 2 + np.random.normal(0, 2), 70, 98)
            promedio_notas = np.clip(5.5 + (clima - 7) * 0.15 + np.random.normal(0, 0.3), 4.0, 7.0)
            
            datos.append({
                'fecha_registro': fecha.isoformat(),
                'periodo': f'Semana {semana + 1}',
                'curso_id': curso_id,
                'clima_escolar_promedio': round(clima, 2),
                'apoyo_docentes_promedio': round(apoyo_docentes, 2),
                'participacion_estudiantes_promedio': round(participacion, 2),
                'nivel_empatia_promedio': round(empatia, 2),
                'nivel_autoestima_promedio': round(autoestima, 2),
                'nivel_resolucion_conflictos_promedio': round(conflictos, 2),
                'incidentes_bullying': int(incidentes_bullying),
                'incidentes_violencia_fisica': int(incidentes_violencia),
                'incidentes_discriminacion': int(incidentes_discriminacion),
                'reportes_anonimos': int(reportes_anonimos),
                'asistencia_promedio_porcentaje': round(asistencia, 2),
                'promedio_notas': round(promedio_notas, 2)
            })
        
        return pd.DataFrame(datos)
    
    def generar_dataset_completo(self):
        """
        Genera dataset completo para todos los cursos con eventos realistas
        """
        cursos_config = [
            ('1°A', 'A', [(10, 'intervencion'), (35, 'intervencion')]),  # Curso con intervenciones
            ('1°B', 'B', [(20, 'crisis')]),  # Curso con crisis no atendida
            ('2°A', 'A', [(15, 'intervencion'), (40, 'intervencion')]),  # Curso con intervenciones
            ('2°B', 'C', [(25, 'crisis')]),  # Curso en deterioro
            ('3°A', 'B', []),  # Curso estable
            ('3°B', 'A', [(12, 'intervencion'), (38, 'intervencion')])   # Curso con intervenciones
        ]
        
        todos_datos = []
        
        for curso_id, tipo, eventos in cursos_config:
            print(f"   Generando datos para {curso_id} (Tipo {tipo})...")
            df_curso = self.generar_serie_temporal_curso(curso_id, tipo, eventos)
            todos_datos.append(df_curso)
        
        return pd.concat(todos_datos, ignore_index=True)


def cargar_datos_cientificos():
    """
    Carga datos científicamente realistas en la base de datos
    """
    print("="*80)
    print("GENERACIÓN DE DATOS CIENTÍFICAMENTE REALISTAS")
    print("="*80)
    print()
    
    # Conectar a BD
    conn = sqlite3.connect('convivir_v4.db')
    cursor = conn.cursor()
    
    # Limpiar datos anteriores
    print("🗑️  Limpiando datos anteriores...")
    cursor.execute("DELETE FROM cursos_temporal")
    cursor.execute("DELETE FROM alertas")
    cursor.execute("DELETE FROM predicciones")
    conn.commit()
    
    # Generar nuevos datos
    print("\n📊 Generando 60 semanas de datos realistas...")
    generador = GeneradorDatosCientificos(n_semanas=60, n_cursos=6)
    df_completo = generador.generar_dataset_completo()
    
    # Insertar en base de datos
    print("\n💾 Insertando en base de datos...")
    for _, row in df_completo.iterrows():
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
            row['fecha_registro'],
            row['periodo'],
            row['curso_id'],
            30,
            row['clima_escolar_promedio'],
            row['apoyo_docentes_promedio'],
            row['participacion_estudiantes_promedio'],
            row['nivel_empatia_promedio'],
            row['nivel_autoestima_promedio'],
            row['nivel_resolucion_conflictos_promedio'],
            row['incidentes_bullying'],
            row['incidentes_violencia_fisica'],
            row['incidentes_discriminacion'],
            row['reportes_anonimos'],
            row['asistencia_promedio_porcentaje'],
            row['promedio_notas']
        ))
    
    conn.commit()
    
    # Estadísticas
    print("\n✅ Datos generados exitosamente")
    print(f"   Total de registros: {len(df_completo)}")
    print(f"   Cursos: {df_completo['curso_id'].nunique()}")
    print(f"   Rango temporal: {df_completo['fecha_registro'].min()} a {df_completo['fecha_registro'].max()}")
    print(f"   Clima promedio: {df_completo['clima_escolar_promedio'].mean():.2f}")
    print(f"   Desviación estándar: {df_completo['clima_escolar_promedio'].std():.2f}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ DATASET CIENTÍFICO LISTO PARA ENTRENAMIENTO")
    print("="*80)


if __name__ == "__main__":
    cargar_datos_cientificos()


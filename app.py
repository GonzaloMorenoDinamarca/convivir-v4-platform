"""
CONVIVIR v4.0 - Plataforma Evolucionada de Innovación Tecnológica
para la Prevención de Violencia Escolar

Versión Web con Datos Precargados
- Datos de ejemplo cargados automáticamente
- Modelo LSTM para predicción de series temporales
- NLP avanzado con análisis de sentimientos
- Graph Neural Networks para análisis de redes sociales
- Sistema de alertas inteligentes
- Dashboard interactivo con simulador de intervenciones
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from sqlalchemy import text

# Importar módulos propios
from database import DatabaseManager
from modelo_lstm import predecir_riesgo_curso, ModeloLSTMPredictor
from modelo_nlp import analizar_sentimientos_establecimiento, AnalizadorNLPAvanzado
from modelo_gnn import analizar_red_social_establecimiento, AnalizadorRedesSociales

app = Flask(__name__)
app.secret_key = 'convivir_v4_secret_key_2025'
app.config['DEBUG'] = False
app.config['ENV'] = 'production'

# Inicializar base de datos
db = DatabaseManager('convivir_v4.db')

# Estado global
estado_analisis = {
    'archivo_cargado': False,
    'nombre_archivo': 'Datos de Ejemplo Precargados',
    'fecha_carga': None,
    'total_estudiantes': 0,
    'total_cursos': 0,
    'total_interacciones': 0,
    'analisis_completados': []
}


def inicializar_datos():
    """Carga datos de ejemplo automáticamente al iniciar"""
    global estado_analisis
    
    # Verificar si ya hay datos
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM estudiantes"))
            count = result.scalar()
            
            if count > 0:
                print("✅ Datos ya cargados en la base de datos")
                estado_analisis['archivo_cargado'] = True
                estado_analisis['total_estudiantes'] = count
                
                # Contar cursos
                result = conn.execute(text("SELECT COUNT(DISTINCT curso_id) FROM cursos_temporal"))
                estado_analisis['total_cursos'] = result.scalar()
                
                # Contar interacciones
                result = conn.execute(text("SELECT COUNT(*) FROM interacciones_sociales"))
                estado_analisis['total_interacciones'] = result.scalar()
                
                return True
    except:
        pass
    
    # Cargar datos de ejemplo
    print("📊 Cargando datos de ejemplo...")
    excel_path = 'CONVIVIR_Formato_Mejorado_Ejemplo.xlsx'
    
    if not os.path.exists(excel_path):
        print("❌ No se encontró el archivo de ejemplo")
        return False
    
    try:
        resultado = db.cargar_desde_excel(excel_path)
        
        if resultado['exito']:
            print("✅ Datos cargados exitosamente")
            estado_analisis['archivo_cargado'] = True
            estado_analisis['fecha_carga'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Contar registros
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM estudiantes"))
                estado_analisis['total_estudiantes'] = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(DISTINCT curso_id) FROM cursos_temporal"))
                estado_analisis['total_cursos'] = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM interacciones_sociales"))
                estado_analisis['total_interacciones'] = result.scalar()
            
            print(f"   📚 Estudiantes: {estado_analisis['total_estudiantes']}")
            print(f"   🎓 Cursos: {estado_analisis['total_cursos']}")
            print(f"   🔗 Interacciones: {estado_analisis['total_interacciones']}")
            return True
        else:
            print(f"❌ Error al cargar datos: {resultado['mensaje']}")
            return False
    
    except Exception as e:
        print(f"❌ Excepción al cargar datos: {e}")
        return False


# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Página principal con dashboard"""
    return render_template('index.html', estado=estado_analisis)


@app.route('/api/estadisticas_generales')
def estadisticas_generales():
    """Obtiene estadísticas generales del establecimiento"""
    try:
        with db.engine.connect() as conn:
            # Estadísticas de estudiantes
            result = conn.execute(text("""
                SELECT COUNT(*) as total
                FROM estudiantes
            """))
            row = result.fetchone()
            total_estudiantes = row[0] if row else 0
            riesgo_promedio = 0
            
            # Estadísticas de cursos
            result = conn.execute(text("""
                SELECT 
                    COUNT(DISTINCT curso_id) as total_cursos,
                    AVG(clima_escolar_promedio) as clima_promedio
                FROM cursos_temporal
            """))
            row = result.fetchone()
            total_cursos = row[0] if row else 0
            clima_promedio = row[1] if row and row[1] else 0
            
            # Alertas pendientes
            result = conn.execute(text("""
                SELECT COUNT(*) FROM alertas WHERE estado = 'pendiente'
            """))
            alertas_pendientes = result.scalar() or 0
            
            # Interacciones registradas
            result = conn.execute(text("SELECT COUNT(*) FROM interacciones_sociales"))
            total_interacciones = result.scalar() or 0
            
            return jsonify({
                'exito': True,
                'total_estudiantes': total_estudiantes,
                'total_cursos': total_cursos,
                'riesgo_promedio': round(float(riesgo_promedio), 2),
                'clima_promedio': round(float(clima_promedio), 2),
                'alertas_pendientes': alertas_pendientes,
                'total_interacciones': total_interacciones
            })
    
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/lista_cursos')
def lista_cursos():
    """Obtiene lista de cursos disponibles"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT DISTINCT curso_id
                FROM cursos_temporal
                ORDER BY curso_id
            """))
            
            cursos = []
            for row in result:
                curso_id = row[0]
                # Extraer nivel y letra del curso_id (ej: "1A" -> nivel=1, letra=A)
                nivel = curso_id[:-1] if curso_id else 'N/A'
                letra = curso_id[-1] if curso_id else ''
                cursos.append({
                    'curso_id': curso_id,
                    'nivel': nivel,
                    'letra': letra
                })
            
            return jsonify({'exito': True, 'cursos': cursos})
    
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/analisis_predictivo/<curso_id>')
def analisis_predictivo_curso(curso_id):
    """Ejecuta análisis predictivo LSTM para un curso"""
    try:
        resultado = predecir_riesgo_curso(db, curso_id, horizonte_semanas=4)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/analisis_sentimientos')
def analisis_sentimientos():
    """Ejecuta análisis de sentimientos NLP"""
    try:
        resultado = analizar_sentimientos_establecimiento(db)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/analisis_red_social')
def analisis_red_social():
    """Ejecuta análisis de red social con GNN"""
    try:
        resultado = analizar_red_social_establecimiento(db)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/alertas')
def obtener_alertas():
    """Obtiene alertas pendientes"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    id,
                    tipo_alerta,
                    nivel_prioridad,
                    estudiante_id,
                    curso_id,
                    mensaje,
                    fecha_creacion,
                    estado
                FROM alertas
                WHERE estado = 'pendiente'
                ORDER BY nivel_prioridad DESC, fecha_creacion DESC
                LIMIT 50
            """))
            
            alertas = []
            for row in result:
                alertas.append({
                    'alerta_id': row[0],
                    'tipo': row[1],
                    'nivel_severidad': row[2],
                    'estudiante_id': row[3],
                    'curso_id': row[4],
                    'descripcion': row[5],
                    'fecha_creacion': str(row[6]),
                    'estado': row[7]
                })
            
            return jsonify({
                'exito': True,
                'alertas': alertas,
                'total': len(alertas)
            })
    
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/simular_intervencion', methods=['POST'])
def simular_intervencion():
    """Simula el impacto de una intervención"""
    try:
        datos = request.json
        curso_id = datos.get('curso_id')
        tipo_intervencion = datos.get('tipo_intervencion', 'Taller de Convivencia')
        impacto_esperado = datos.get('impacto_esperado', 0.15)  # 15% de mejora por defecto
        
        # Obtener datos históricos
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT fecha_registro, clima_escolar_promedio, nivel_empatia_promedio, nivel_resolucion_conflictos_promedio
                FROM cursos_temporal
                WHERE curso_id = :curso_id
                ORDER BY fecha_registro
            """), {'curso_id': curso_id})
            
            rows = result.fetchall()
            if len(rows) < 4:
                return jsonify({'exito': False, 'mensaje': 'Datos insuficientes para simulación'})
            
            data = pd.DataFrame(rows, columns=['fecha', 'clima_escolar', 'nivel_empatia', 'gestion_conflictos'])
        
        # Crear modelo
        modelo = ModeloLSTMPredictor(sequence_length=4, horizonte_prediccion=4)
        
        # Entrenar modelo
        modelo.entrenar(data, target_col='clima_escolar', epochs=20)
        
        # Predicción sin intervención
        pred_sin = modelo.predecir(data, target_col='clima_escolar')
        
        # Simular intervención: modificar últimos valores
        data_modificado = data.copy()
        data_modificado.loc[data_modificado.index[-2:], 'clima_escolar'] *= (1 + impacto_esperado)
        data_modificado.loc[data_modificado.index[-2:], 'nivel_empatia'] *= (1 + impacto_esperado * 0.8)
        data_modificado.loc[data_modificado.index[-2:], 'gestion_conflictos'] *= (1 + impacto_esperado * 0.7)
        
        # Predicción con intervención
        pred_con = modelo.predecir(data_modificado, target_col='clima_escolar')
        
        mejora = [
            round(pred_con['predicciones'][i] - pred_sin['predicciones'][i], 2)
            for i in range(len(pred_sin['predicciones']))
        ]
        
        return jsonify({
            'exito': True,
            'curso_id': curso_id,
            'tipo_intervencion': tipo_intervencion,
            'prediccion_sin_intervencion': [round(p, 2) for p in pred_sin['predicciones']],
            'prediccion_con_intervencion': [round(p, 2) for p in pred_con['predicciones']],
            'mejora_esperada': mejora,
            'mejora_promedio': round(sum(mejora) / len(mejora), 2)
        })
    
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/grafico_evolucion/<curso_id>')
def grafico_evolucion(curso_id):
    """Genera gráfico de evolución temporal"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT fecha_registro, clima_escolar_promedio, nivel_empatia_promedio, nivel_resolucion_conflictos_promedio
                FROM cursos_temporal
                WHERE curso_id = :curso_id
                ORDER BY fecha_registro
            """), {'curso_id': curso_id})
            
            rows = result.fetchall()
            data = pd.DataFrame(rows, columns=['fecha', 'clima_escolar', 'nivel_empatia', 'gestion_conflictos'])
        
        # Crear figura
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['fecha'],
            y=data['clima_escolar'],
            mode='lines+markers',
            name='Clima Escolar',
            line=dict(color='#4CAF50', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=data['fecha'],
            y=data['nivel_empatia'],
            mode='lines+markers',
            name='Nivel de Empatía',
            line=dict(color='#2196F3', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=data['fecha'],
            y=data['gestion_conflictos'],
            mode='lines+markers',
            name='Gestión de Conflictos',
            line=dict(color='#FF9800', width=3)
        ))
        
        fig.update_layout(
            title=f'Evolución Temporal - Curso {curso_id}',
            xaxis_title='Fecha',
            yaxis_title='Indicador (1-10)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig.to_json()
    
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/grafico_red_social')
def grafico_red_social():
    """Genera visualización de red social"""
    try:
        resultado = analizar_red_social_establecimiento(db)
        
        if not resultado['exito']:
            return jsonify({'error': resultado['mensaje']})
        
        # Crear grafo de red
        G = resultado['grafo']
        
        # Posiciones de nodos
        import networkx as nx
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Extraer coordenadas
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Estudiante {node}<br>Conexiones: {G.degree(node)}")
            node_color.append(G.degree(node))
        
        # Crear figura
        fig = go.Figure()
        
        # Aristas
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Nodos
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(
                size=10,
                color=node_color,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Conexiones")
            ),
            text=node_text,
            hoverinfo='text',
            showlegend=False
        ))
        
        fig.update_layout(
            title='Red Social del Establecimiento',
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
        
        return fig.to_json()
    
    except Exception as e:
        return jsonify({'error': str(e)})


# ============================================================================
# EJECUTAR APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("🎓 CONVIVIR v4.0 - Plataforma Evolucionada")
    print("=" * 80)
    print()
    
    # Inicializar datos
    if inicializar_datos():
        print()
        print("=" * 80)
        print("✅ Sistema listo para usar")
        print("=" * 80)
        print()
        print("🌐 Acceda a la aplicación en: http://localhost:5000")
        print()
        print("=" * 80)
    else:
        print()
        print("=" * 80)
        print("⚠️  Sistema iniciado sin datos")
        print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)




# ==================== RUTAS PARA INGRESO DE DATOS EN TIEMPO REAL ====================

@app.route('/ingresar_datos')
def pagina_ingresar_datos():
    """Página de formulario para ingresar datos semanales"""
    return render_template('ingresar_datos.html')


@app.route('/api/progreso_datos', methods=['GET'])
def api_progreso_datos():
    """Retorna el progreso de recolección de datos"""
    try:
        with db.get_session() as session:
            # Contar semanas únicas registradas
            query = text("""
                SELECT COUNT(DISTINCT fecha_registro) as semanas
                FROM cursos_temporal
            """)
            result = session.execute(query).fetchone()
            semanas_registradas = result[0] if result else 0
            
            # Calcular confiabilidad
            confiabilidad = 'BAJA'
            if semanas_registradas >= 52:
                confiabilidad = 'ALTA'
            elif semanas_registradas >= 26:
                confiabilidad = 'MEDIA'
            
            return jsonify({
                'exito': True,
                'semanas_registradas': semanas_registradas,
                'semanas_requeridas': 52,
                'porcentaje': min((semanas_registradas / 52) * 100, 100),
                'confiabilidad': confiabilidad
            })
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/ingresar_datos_semanales', methods=['POST'])
def api_ingresar_datos_semanales():
    """Recibe y guarda datos semanales del formulario"""
    try:
        data = request.json
        
        # Validar datos requeridos
        campos_requeridos = [
            'fecha', 'curso', 'periodo', 'clima_escolar', 'apoyo_docentes',
            'participacion', 'empatia', 'autoestima', 'resolucion_conflictos',
            'incidentes_bullying', 'incidentes_violencia', 'incidentes_discriminacion',
            'reportes_anonimos', 'asistencia', 'promedio_notas'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] == '':
                return jsonify({
                    'exito': False,
                    'mensaje': f'Campo requerido faltante: {campo}'
                })
        
        # Insertar en base de datos
        with db.get_session() as session:
            query = text("""
                INSERT INTO cursos_temporal (
                    establecimiento_id, fecha_registro, periodo, curso_id,
                    total_estudiantes, clima_escolar_promedio, apoyo_docentes_promedio,
                    participacion_estudiantes_promedio, nivel_empatia_promedio,
                    nivel_autoestima_promedio, nivel_resolucion_conflictos_promedio,
                    incidentes_bullying, incidentes_violencia_fisica, incidentes_discriminacion,
                    reportes_anonimos, asistencia_promedio_porcentaje, promedio_notas
                ) VALUES (
                    :establecimiento_id, :fecha_registro, :periodo, :curso_id,
                    :total_estudiantes, :clima_escolar, :apoyo_docentes,
                    :participacion, :empatia, :autoestima, :resolucion_conflictos,
                    :incidentes_bullying, :incidentes_violencia, :incidentes_discriminacion,
                    :reportes_anonimos, :asistencia, :promedio_notas
                )
            """)
            
            session.execute(query, {
                'establecimiento_id': 'EST_001',
                'fecha_registro': data['fecha'],
                'periodo': data['periodo'],
                'curso_id': data['curso'],
                'total_estudiantes': 30,  # Valor por defecto
                'clima_escolar': float(data['clima_escolar']),
                'apoyo_docentes': float(data['apoyo_docentes']),
                'participacion': float(data['participacion']),
                'empatia': float(data['empatia']),
                'autoestima': float(data['autoestima']),
                'resolucion_conflictos': float(data['resolucion_conflictos']),
                'incidentes_bullying': int(data['incidentes_bullying']),
                'incidentes_violencia': int(data['incidentes_violencia']),
                'incidentes_discriminacion': int(data['incidentes_discriminacion']),
                'reportes_anonimos': int(data['reportes_anonimos']),
                'asistencia': float(data['asistencia']),
                'promedio_notas': float(data['promedio_notas'])
            })
            
            session.commit()
            
            # Si hay evento, registrarlo
            if data.get('tipo_evento') and data.get('tipo_evento') != '':
                query_evento = text("""
                    INSERT INTO intervenciones (
                        establecimiento_id, curso_id, fecha_aplicacion,
                        tipo_intervencion, descripcion, responsable
                    ) VALUES (
                        :establecimiento_id, :curso_id, :fecha,
                        :tipo, :descripcion, 'Sistema'
                    )
                """)
                
                session.execute(query_evento, {
                    'establecimiento_id': 'EST_001',
                    'curso_id': data['curso'],
                    'fecha': data['fecha'],
                    'tipo': data['tipo_evento'],
                    'descripcion': data.get('descripcion_evento', '')
                })
                
                session.commit()
            
            # Contar total de semanas
            query_count = text("""
                SELECT COUNT(DISTINCT fecha_registro) as semanas
                FROM cursos_temporal
            """)
            result = session.execute(query_count).fetchone()
            semanas_totales = result[0] if result else 0
            
            # Si hay suficientes datos, reentrenar modelo
            if semanas_totales >= 12:
                try:
                    from modelo_ensemble_robusto import ModeloEnsembleRobusto
                    
                    # Cargar datos para reentrenamiento
                    query_datos = text("""
                        SELECT fecha_registro, clima_escolar_promedio
                        FROM cursos_temporal
                        WHERE curso_id = :curso_id
                        ORDER BY fecha_registro
                    """)
                    df = pd.read_sql_query(query_datos, session.bind, params={'curso_id': data['curso']})
                    
                    if len(df) >= 12:
                        modelo = ModeloEnsembleRobusto(horizonte_prediccion=4, sequence_length=8)
                        modelo.entrenar_con_validacion(df, target_col='clima_escolar_promedio')
                        
                        # Guardar modelo (simplificado - en producción usar pickle)
                        print(f"✅ Modelo reentrenado para {data['curso']} con {len(df)} semanas")
                except Exception as e:
                    print(f"⚠️ No se pudo reentrenar modelo: {e}")
            
            return jsonify({
                'exito': True,
                'mensaje': 'Datos guardados exitosamente',
                'semanas_totales': semanas_totales,
                'curso': data['curso'],
                'fecha': data['fecha']
            })
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al guardar datos: {str(e)}'
        })


@app.route('/api/estadisticas_recoleccion', methods=['GET'])
def api_estadisticas_recoleccion():
    """Estadísticas de recolección de datos por curso"""
    try:
        with db.get_session() as session:
            query = text("""
                SELECT 
                    curso_id,
                    COUNT(*) as total_registros,
                    MIN(fecha_registro) as fecha_inicio,
                    MAX(fecha_registro) as fecha_ultima,
                    AVG(clima_escolar_promedio) as clima_promedio
                FROM cursos_temporal
                GROUP BY curso_id
                ORDER BY curso_id
            """)
            
            resultados = session.execute(query).fetchall()
            
            estadisticas = []
            for row in resultados:
                estadisticas.append({
                    'curso': row[0],
                    'registros': row[1],
                    'fecha_inicio': row[2],
                    'fecha_ultima': row[3],
                    'clima_promedio': round(row[4], 2) if row[4] else 0
                })
            
            return jsonify({
                'exito': True,
                'estadisticas': estadisticas
            })
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})




# ==================== GESTIÓN DE CURSOS MÚLTIPLES ====================

@app.route('/configurar_cursos')
def pagina_configurar_cursos():
    """Página de configuración de cursos"""
    return render_template('configurar_cursos.html')


@app.route('/api/listar_cursos', methods=['GET'])
def api_listar_cursos():
    """Lista todos los cursos configurados"""
    try:
        with db.get_session() as session:
            # Obtener cursos únicos con estadísticas
            query = text("""
                SELECT 
                    curso_id,
                    MAX(total_estudiantes) as total_estudiantes,
                    COUNT(DISTINCT fecha_registro) as semanas_registradas
                FROM cursos_temporal
                GROUP BY curso_id
                ORDER BY curso_id
            """)
            
            resultados = session.execute(query).fetchall()
            
            cursos = []
            for row in resultados:
                cursos.append({
                    'id': row[0],
                    'nombre': row[0],
                    'total_estudiantes': row[1] or 30,
                    'semanas_registradas': row[2] or 0
                })
            
            return jsonify({
                'exito': True,
                'cursos': cursos,
                'total': len(cursos)
            })
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/agregar_curso', methods=['POST'])
def api_agregar_curso():
    """Agrega un nuevo curso al sistema"""
    try:
        data = request.json
        
        if not data.get('nombre_curso'):
            return jsonify({'exito': False, 'mensaje': 'Nombre de curso requerido'})
        
        nombre_curso = data['nombre_curso'].strip()
        total_estudiantes = int(data.get('total_estudiantes', 30))
        
        # Verificar si el curso ya existe
        with db.get_session() as session:
            query_check = text("""
                SELECT COUNT(*) as count
                FROM cursos_temporal
                WHERE curso_id = :curso_id
            """)
            result = session.execute(query_check, {'curso_id': nombre_curso}).fetchone()
            
            if result[0] > 0:
                return jsonify({
                    'exito': False,
                    'mensaje': f'El curso "{nombre_curso}" ya existe'
                })
            
            # Crear registro inicial del curso
            query_insert = text("""
                INSERT INTO cursos_temporal (
                    establecimiento_id, fecha_registro, periodo, curso_id,
                    total_estudiantes, clima_escolar_promedio, apoyo_docentes_promedio,
                    participacion_estudiantes_promedio, nivel_empatia_promedio,
                    nivel_autoestima_promedio, nivel_resolucion_conflictos_promedio,
                    incidentes_bullying, incidentes_violencia_fisica, incidentes_discriminacion,
                    reportes_anonimos, asistencia_promedio_porcentaje, promedio_notas
                ) VALUES (
                    'EST_001', :fecha, 'Configuración Inicial', :curso_id,
                    :total_estudiantes, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                    0, 0, 0, 0, 85.0, 5.0
                )
            """)
            
            session.execute(query_insert, {
                'fecha': datetime.now().strftime('%Y-%m-%d'),
                'curso_id': nombre_curso,
                'total_estudiantes': total_estudiantes
            })
            
            session.commit()
            
            return jsonify({
                'exito': True,
                'mensaje': f'Curso "{nombre_curso}" agregado exitosamente',
                'curso': {
                    'id': nombre_curso,
                    'nombre': nombre_curso,
                    'total_estudiantes': total_estudiantes
                }
            })
            
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': f'Error al agregar curso: {str(e)}'})


@app.route('/api/eliminar_curso', methods=['POST'])
def api_eliminar_curso():
    """Elimina un curso y todos sus datos"""
    try:
        data = request.json
        curso_id = data.get('curso_id')
        
        if not curso_id:
            return jsonify({'exito': False, 'mensaje': 'ID de curso requerido'})
        
        with db.get_session() as session:
            # Eliminar datos temporales del curso
            query_delete_temporal = text("""
                DELETE FROM cursos_temporal
                WHERE curso_id = :curso_id
            """)
            session.execute(query_delete_temporal, {'curso_id': curso_id})
            
            # Eliminar intervenciones del curso
            query_delete_intervenciones = text("""
                DELETE FROM intervenciones
                WHERE curso_id = :curso_id
            """)
            session.execute(query_delete_intervenciones, {'curso_id': curso_id})
            
            session.commit()
            
            return jsonify({
                'exito': True,
                'mensaje': f'Curso "{curso_id}" eliminado exitosamente'
            })
            
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': f'Error al eliminar curso: {str(e)}'})


@app.route('/api/cursos_disponibles', methods=['GET'])
def api_cursos_disponibles():
    """Retorna lista de cursos para selectores"""
    try:
        with db.get_session() as session:
            query = text("""
                SELECT DISTINCT curso_id
                FROM cursos_temporal
                ORDER BY curso_id
            """)
            
            resultados = session.execute(query).fetchall()
            cursos = [row[0] for row in resultados]
            
            return jsonify({
                'exito': True,
                'cursos': cursos
            })
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})



@app.route('/api/generar_reporte', methods=['GET'])
def api_generar_reporte():
    """Genera un reporte completo del establecimiento"""
    try:
        # Obtener estadísticas generales
        with db.get_session() as session:
            # Contar registros
            total_estudiantes = session.execute(text("SELECT COUNT(*) FROM estudiantes")).scalar()
            total_cursos = session.execute(text("SELECT COUNT(DISTINCT curso_id) FROM cursos_temporal")).scalar()
            total_interacciones = session.execute(text("SELECT COUNT(*) FROM interacciones_sociales")).scalar()
            total_alertas = session.execute(text("SELECT COUNT(*) FROM alertas WHERE estado='pendiente'")).scalar()
            
            # Calcular promedios
            clima_promedio = session.execute(text(
                "SELECT AVG(clima_escolar_promedio) FROM cursos_temporal"
            )).scalar() or 0
            
            # Contar semanas de datos
            semanas_datos = session.execute(text(
                "SELECT COUNT(DISTINCT fecha_registro) FROM cursos_temporal"
            )).scalar() or 0
            
            reporte_resumen = {
                'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_estudiantes': total_estudiantes,
                'total_cursos': total_cursos,
                'total_interacciones': total_interacciones,
                'alertas_pendientes': total_alertas,
                'clima_promedio': round(clima_promedio, 2),
                'semanas_datos_recolectados': semanas_datos,
                'confiabilidad': 'BAJA' if semanas_datos < 12 else 'MEDIA' if semanas_datos < 52 else 'ALTA'
            }
            
            return jsonify({
                'exito': True,
                'mensaje': f'Reporte generado exitosamente. Se han analizado {total_estudiantes} estudiantes en {total_cursos} cursos con {semanas_datos} semanas de datos.',
                'reporte': reporte_resumen
            })
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al generar reporte: {str(e)}'
        })


# ============================================================================
# INICIO DE LA APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("🎓 CONVIVIR v4.0 - Plataforma Evolucionada")
    print("=" * 80)
    
    # Inicializar datos solo en el proceso principal
    inicializar_datos()
    
    print("=" * 80)
    print("✅ Sistema listo para usar")
    print("=" * 80)
    
    # Obtener puerto desde variable de entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Acceda a la aplicación en: http://localhost:{port}")
    print("=" * 80)
    
    # Iniciar servidor en modo producción (sin debug, sin reloader)
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


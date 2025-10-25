"""
CONVIVIR v4.0 - Plataforma Evolucionada de Innovación Tecnológica
para la Prevención de Violencia Escolar

Incluye:
- Soporte para formato Excel mejorado (8 hojas)
- Modelo LSTM para predicción de series temporales
- NLP avanzado con transformers
- Graph Neural Networks para análisis de redes sociales
- Sistema de alertas inteligentes
- Dashboard interactivo con simulador de intervenciones
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

# Importar módulos propios
from database import DatabaseManager
from modelo_lstm import predecir_riesgo_curso, ModeloLSTMPredictor
from modelo_nlp import analizar_sentimientos_establecimiento, AnalizadorNLPAvanzado
from modelo_gnn import analizar_red_social_establecimiento, AnalizadorRedesSociales

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.secret_key = 'convivir_v4_secret_key_2025'

# Crear carpetas necesarias
os.makedirs('uploads', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Inicializar base de datos
db = DatabaseManager('convivir_v4.db')

# Estado global
estado_analisis = {
    'archivo_cargado': False,
    'nombre_archivo': None,
    'fecha_carga': None,
    'total_estudiantes': 0,
    'total_cursos': 0,
    'analisis_completados': []
}


# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html', estado=estado_analisis)


@app.route('/cargar_datos', methods=['GET', 'POST'])
def cargar_datos():
    """Carga de datos desde Excel"""
    if request.method == 'GET':
        return render_template('cargar_datos.html')
    
    if 'archivo' not in request.files:
        return jsonify({'exito': False, 'mensaje': 'No se recibió ningún archivo'})
    
    archivo = request.files['archivo']
    
    if archivo.filename == '':
        return jsonify({'exito': False, 'mensaje': 'No se seleccionó ningún archivo'})
    
    if not archivo.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'exito': False, 'mensaje': 'El archivo debe ser formato Excel (.xlsx o .xls)'})
    
    try:
        # Guardar archivo
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
        archivo.save(filepath)
        
        # Cargar a base de datos
        resultado = db.cargar_desde_excel(filepath)
        
        if resultado['exito']:
            # Actualizar estado
            estado_analisis['archivo_cargado'] = True
            estado_analisis['nombre_archivo'] = archivo.filename
            estado_analisis['fecha_carga'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Contar estudiantes y cursos
            estado_analisis['total_estudiantes'] = db.session.query(db.session.query(type('Estudiante', (), {})).from_statement(
                "SELECT COUNT(*) as count FROM estudiantes"
            ).first()).count if hasattr(db.session.query(type('Estudiante', (), {})).from_statement(
                "SELECT COUNT(*) as count FROM estudiantes"
            ).first(), 'count') else 0
            
            return jsonify({
                'exito': True,
                'mensaje': 'Datos cargados exitosamente',
                'detalles': resultado
            })
        else:
            return jsonify(resultado)
    
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': f'Error al procesar archivo: {str(e)}'})


@app.route('/dashboard')
def dashboard():
    """Dashboard principal con visualizaciones"""
    if not estado_analisis['archivo_cargado']:
        return redirect(url_for('cargar_datos'))
    
    return render_template('dashboard.html', estado=estado_analisis)


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
        alertas_df = db.obtener_alertas_pendientes()
        return jsonify({
            'exito': True,
            'alertas': alertas_df.to_dict('records'),
            'total': len(alertas_df)
        })
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/simular_intervencion', methods=['POST'])
def simular_intervencion():
    """Simula el impacto de una intervención"""
    try:
        datos = request.json
        curso_id = datos.get('curso_id')
        tipo_intervencion = datos.get('tipo_intervencion')
        impacto_esperado = datos.get('impacto_esperado', 0.1)  # 10% de mejora por defecto
        
        # Obtener datos históricos
        data = db.obtener_series_temporales_curso(curso_id)
        
        if len(data) < 4:
            return jsonify({'exito': False, 'mensaje': 'Datos insuficientes'})
        
        # Crear modelo
        modelo = ModeloLSTMPredictor(sequence_length=4, horizonte_prediccion=4)
        
        # Entrenar modelo
        modelo.entrenar(data, target_col='clima_escolar', epochs=30)
        
        # Predicción sin intervención
        pred_sin = modelo.predecir(data, target_col='clima_escolar')
        
        # Simular intervención: modificar últimos valores
        data_modificado = data.copy()
        data_modificado.loc[data_modificado.index[-2:], 'clima_escolar'] *= (1 + impacto_esperado)
        data_modificado.loc[data_modificado.index[-2:], 'nivel_empatia'] *= (1 + impacto_esperado * 0.8)
        
        # Predicción con intervención
        pred_con = modelo.predecir(data_modificado, target_col='clima_escolar')
        
        return jsonify({
            'exito': True,
            'curso_id': curso_id,
            'tipo_intervencion': tipo_intervencion,
            'prediccion_sin_intervencion': pred_sin['predicciones'],
            'prediccion_con_intervencion': pred_con['predicciones'],
            'mejora_esperada': [
                pred_con['predicciones'][i] - pred_sin['predicciones'][i]
                for i in range(len(pred_sin['predicciones']))
            ]
        })
    
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})


@app.route('/api/grafico_prediccion/<curso_id>')
def grafico_prediccion(curso_id):
    """Genera gráfico de predicción temporal"""
    try:
        # Obtener datos históricos
        data = db.obtener_series_temporales_curso(curso_id)
        
        # Crear figura
        fig = go.Figure()
        
        # Datos históricos
        fig.add_trace(go.Scatter(
            x=data['fecha'],
            y=data['clima_escolar'],
            mode='lines+markers',
            name='Histórico',
            line=dict(color='blue', width=2)
        ))
        
        # Obtener predicción
        resultado = predecir_riesgo_curso(db, curso_id, horizonte_semanas=4)
        
        if resultado['exito']:
            pred = resultado['predicciones']
            
            # Fechas futuras
            ultima_fecha = data['fecha'].max()
            fechas_futuras = [ultima_fecha + timedelta(weeks=i+1) for i in range(len(pred['predicciones']))]
            
            # Predicción
            fig.add_trace(go.Scatter(
                x=fechas_futuras,
                y=pred['predicciones'],
                mode='lines+markers',
                name='Predicción',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            # Intervalo de confianza
            fig.add_trace(go.Scatter(
                x=fechas_futuras + fechas_futuras[::-1],
                y=pred['intervalo_confianza_superior'] + pred['intervalo_confianza_inferior'][::-1],
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(color='rgba(255,0,0,0)'),
                name='Intervalo de Confianza',
                showlegend=True
            ))
        
        fig.update_layout(
            title=f'Predicción de Clima Escolar - Curso {curso_id}',
            xaxis_title='Fecha',
            yaxis_title='Clima Escolar (1-10)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig.to_json()
    
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/alertas')
def pagina_alertas():
    """Página de alertas"""
    return render_template('alertas.html')


@app.route('/simulador')
def pagina_simulador():
    """Página del simulador de intervenciones"""
    return render_template('simulador.html')


@app.route('/red_social')
def pagina_red_social():
    """Página de análisis de red social"""
    return render_template('red_social.html')


# ============================================================================
# EJECUTAR APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("CONVIVIR v4.0 - Plataforma Evolucionada")
    print("=" * 80)
    print("Iniciando servidor Flask...")
    print("Acceda a la aplicación en: http://localhost:5000")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)


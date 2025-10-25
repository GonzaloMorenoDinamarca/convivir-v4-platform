"""
Módulo de Análisis NLP Avanzado con Transformers
Análisis de sentimientos mejorado para comentarios de estudiantes
"""

import numpy as np
import pandas as pd
from collections import Counter
import re
import warnings
warnings.filterwarnings('ignore')

# Intentar importar transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers no disponible. Usando análisis basado en reglas.")


class AnalizadorNLPAvanzado:
    """
    Analizador de sentimientos avanzado con soporte para modelos transformer
    """
    
    def __init__(self, usar_transformer=True):
        """
        Args:
            usar_transformer: Si True, intenta usar modelos transformer. Si False o no disponible, usa reglas.
        """
        self.usar_transformer = usar_transformer and TRANSFORMERS_AVAILABLE
        self.sentiment_pipeline = None
        
        if self.usar_transformer:
            try:
                # Intentar cargar modelo en español
                # Opciones: 'pysentimiento/robertuito-sentiment-analysis', 'finiteautomata/beto-sentiment-analysis'
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="finiteautomata/beto-sentiment-analysis",
                    truncation=True,
                    max_length=512
                )
                print("✅ Modelo transformer cargado exitosamente")
            except Exception as e:
                print(f"⚠️ Error al cargar transformer: {e}. Usando análisis basado en reglas.")
                self.usar_transformer = False
        
        # Diccionarios de palabras clave (backup y para análisis temático)
        self.palabras_positivas = {
            'bien', 'bueno', 'excelente', 'feliz', 'contento', 'alegre', 'amigos',
            'apoyo', 'seguro', 'tranquilo', 'respeto', 'valorado', 'querido',
            'divertido', 'agradable', 'cómodo', 'confianza', 'motivado'
        }
        
        self.palabras_negativas = {
            'mal', 'malo', 'triste', 'solo', 'aislado', 'miedo', 'ansiedad',
            'bullying', 'acoso', 'molestan', 'insultan', 'rechazo', 'violencia',
            'discriminación', 'abuso', 'amenaza', 'pelea', 'conflicto', 'problema',
            'odio', 'enojo', 'frustrado', 'preocupado', 'estresado'
        }
        
        self.temas_keywords = {
            'bullying': ['bullying', 'acoso', 'molestan', 'insultan', 'burlan', 'amenaza'],
            'violencia': ['violencia', 'pelea', 'golpe', 'agresión', 'física'],
            'discriminación': ['discriminación', 'racismo', 'exclusión', 'rechazo'],
            'clima_escolar': ['ambiente', 'clima', 'escuela', 'colegio', 'institución'],
            'relaciones': ['amigos', 'compañeros', 'relación', 'grupo', 'amistad'],
            'emociones': ['siento', 'emoción', 'feliz', 'triste', 'miedo', 'ansiedad'],
            'apoyo_docente': ['profesor', 'docente', 'maestro', 'apoyo', 'ayuda']
        }
    
    def analizar_sentimiento(self, texto):
        """
        Analiza el sentimiento de un texto
        
        Args:
            texto: String con el comentario a analizar
        
        Returns:
            dict con sentimiento, confianza y método usado
        """
        if not texto or len(str(texto).strip()) == 0:
            return {
                'sentimiento': 'neutral',
                'confianza': 0.0,
                'metodo': 'texto_vacio'
            }
        
        texto = str(texto).lower().strip()
        
        if self.usar_transformer and self.sentiment_pipeline:
            try:
                # Análisis con transformer
                resultado = self.sentiment_pipeline(texto[:512])[0]  # Limitar longitud
                
                # Mapear etiquetas (pueden variar según el modelo)
                label_map = {
                    'POS': 'positivo',
                    'NEG': 'negativo',
                    'NEU': 'neutral',
                    'POSITIVE': 'positivo',
                    'NEGATIVE': 'negativo',
                    'NEUTRAL': 'neutral'
                }
                
                sentimiento = label_map.get(resultado['label'].upper(), 'neutral')
                confianza = resultado['score']
                
                return {
                    'sentimiento': sentimiento,
                    'confianza': float(confianza),
                    'metodo': 'transformer'
                }
            
            except Exception as e:
                print(f"Error en transformer, usando reglas: {e}")
                # Fallback a reglas
                return self._analizar_con_reglas(texto)
        
        else:
            # Análisis basado en reglas
            return self._analizar_con_reglas(texto)
    
    def _analizar_con_reglas(self, texto):
        """Análisis de sentimientos basado en reglas y palabras clave"""
        palabras = set(re.findall(r'\b\w+\b', texto.lower()))
        
        # Contar palabras positivas y negativas
        count_pos = len(palabras & self.palabras_positivas)
        count_neg = len(palabras & self.palabras_negativas)
        
        # Determinar sentimiento
        if count_pos > count_neg:
            sentimiento = 'positivo'
            confianza = min(0.6 + (count_pos - count_neg) * 0.1, 0.95)
        elif count_neg > count_pos:
            sentimiento = 'negativo'
            confianza = min(0.6 + (count_neg - count_pos) * 0.1, 0.95)
        else:
            sentimiento = 'neutral'
            confianza = 0.5
        
        return {
            'sentimiento': sentimiento,
            'confianza': float(confianza),
            'metodo': 'reglas'
        }
    
    def extraer_temas(self, texto):
        """
        Extrae temas principales del texto
        
        Returns:
            list de temas detectados
        """
        texto = str(texto).lower()
        temas_detectados = []
        
        for tema, keywords in self.temas_keywords.items():
            for keyword in keywords:
                if keyword in texto:
                    temas_detectados.append(tema)
                    break
        
        return temas_detectados if temas_detectados else ['general']
    
    def analizar_comentarios_batch(self, df_comentarios):
        """
        Analiza un lote de comentarios
        
        Args:
            df_comentarios: DataFrame con columna 'texto'
        
        Returns:
            DataFrame con análisis agregado
        """
        resultados = []
        
        for idx, row in df_comentarios.iterrows():
            texto = row.get('texto', row.get('comentario_texto', ''))
            
            # Analizar sentimiento
            analisis_sent = self.analizar_sentimiento(texto)
            
            # Extraer temas
            temas = self.extraer_temas(texto)
            
            resultados.append({
                'id': row.get('id', idx),
                'estudiante_id': row.get('estudiante_id', None),
                'texto': texto,
                'sentimiento': analisis_sent['sentimiento'],
                'confianza': analisis_sent['confianza'],
                'metodo': analisis_sent['metodo'],
                'temas': temas,
                'tema_principal': temas[0] if temas else 'general'
            })
        
        return pd.DataFrame(resultados)
    
    def generar_reporte_sentimientos(self, df_resultados):
        """
        Genera un reporte agregado de sentimientos
        
        Returns:
            dict con estadísticas
        """
        # Distribución de sentimientos
        distribucion = df_resultados['sentimiento'].value_counts().to_dict()
        
        # Confianza promedio
        confianza_promedio = df_resultados['confianza'].mean()
        
        # Temas más frecuentes
        todos_temas = []
        for temas in df_resultados['temas']:
            todos_temas.extend(temas)
        temas_frecuentes = Counter(todos_temas).most_common(5)
        
        # Estudiantes con sentimiento negativo
        estudiantes_negativos = df_resultados[
            df_resultados['sentimiento'] == 'negativo'
        ]['estudiante_id'].unique().tolist()
        
        # Comentarios prioritarios (negativos con alta confianza)
        comentarios_prioritarios = df_resultados[
            (df_resultados['sentimiento'] == 'negativo') & 
            (df_resultados['confianza'] > 0.7)
        ].to_dict('records')
        
        return {
            'distribucion_sentimientos': distribucion,
            'confianza_promedio': float(confianza_promedio),
            'temas_frecuentes': temas_frecuentes,
            'total_comentarios': len(df_resultados),
            'estudiantes_con_sentimiento_negativo': estudiantes_negativos,
            'total_estudiantes_negativos': len(estudiantes_negativos),
            'comentarios_prioritarios': comentarios_prioritarios[:10],  # Top 10
            'metodo_analisis': df_resultados['metodo'].iloc[0] if len(df_resultados) > 0 else 'ninguno'
        }
    
    def identificar_estudiantes_riesgo(self, df_resultados, umbral_negativos=2):
        """
        Identifica estudiantes en riesgo basándose en comentarios negativos recurrentes
        
        Args:
            df_resultados: DataFrame con resultados de análisis
            umbral_negativos: Número mínimo de comentarios negativos para considerar en riesgo
        
        Returns:
            DataFrame con estudiantes en riesgo
        """
        # Filtrar comentarios negativos
        negativos = df_resultados[df_resultados['sentimiento'] == 'negativo']
        
        # Contar por estudiante
        conteo = negativos.groupby('estudiante_id').agg({
            'id': 'count',
            'confianza': 'mean',
            'temas': lambda x: list(set([t for temas in x for t in temas]))
        }).rename(columns={'id': 'comentarios_negativos', 'confianza': 'confianza_promedio'})
        
        # Filtrar por umbral
        en_riesgo = conteo[conteo['comentarios_negativos'] >= umbral_negativos]
        en_riesgo = en_riesgo.sort_values('comentarios_negativos', ascending=False)
        
        return en_riesgo.reset_index()


def analizar_sentimientos_establecimiento(db_manager):
    """
    Función de alto nivel para analizar sentimientos de todo el establecimiento
    
    Args:
        db_manager: Instancia de DatabaseManager
    
    Returns:
        dict con análisis completo
    """
    # Obtener comentarios
    df_comentarios = db_manager.obtener_comentarios_para_nlp()
    
    if len(df_comentarios) == 0:
        return {
            'exito': False,
            'mensaje': 'No hay comentarios disponibles para analizar'
        }
    
    # Crear analizador
    analizador = AnalizadorNLPAvanzado(usar_transformer=True)
    
    # Analizar comentarios
    df_resultados = analizador.analizar_comentarios_batch(df_comentarios)
    
    # Generar reporte
    reporte = analizador.generar_reporte_sentimientos(df_resultados)
    
    # Identificar estudiantes en riesgo
    estudiantes_riesgo = analizador.identificar_estudiantes_riesgo(df_resultados, umbral_negativos=2)
    
    # Actualizar base de datos con resultados
    for _, row in df_resultados.iterrows():
        comentario = db_manager.session.query(db_manager.session.query(type('Comentario', (), {})).from_statement(
            f"SELECT * FROM comentarios WHERE id = {row['id']}"
        ).first())
        
        # Nota: Esto es una simplificación. En producción, usar ORM correctamente.
    
    # Generar alertas para estudiantes en riesgo
    for _, estudiante in estudiantes_riesgo.iterrows():
        mensaje = f"El estudiante {estudiante['estudiante_id']} ha tenido {estudiante['comentarios_negativos']} comentarios con sentimiento negativo."
        recomendacion = f"Se recomienda entrevista individual. Temas detectados: {', '.join(estudiante['temas'][:3])}"
        
        db_manager.crear_alerta(
            tipo_alerta='sentimiento',
            nivel_prioridad='alta' if estudiante['comentarios_negativos'] >= 3 else 'media',
            mensaje=mensaje,
            recomendacion=recomendacion,
            estudiante_id=estudiante['estudiante_id']
        )
    
    return {
        'exito': True,
        'reporte_general': reporte,
        'estudiantes_en_riesgo': estudiantes_riesgo.to_dict('records'),
        'total_estudiantes_riesgo': len(estudiantes_riesgo),
        'resultados_detallados': df_resultados.to_dict('records')
    }


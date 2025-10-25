"""
Módulo de Modelo LSTM para Predicción de Series Temporales
Predice la evolución futura de indicadores de convivencia escolar
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow no disponible. Usando modelo simplificado.")


class ModeloLSTMPredictor:
    """
    Modelo LSTM para predecir series temporales de indicadores de convivencia
    """
    
    def __init__(self, sequence_length=4, horizonte_prediccion=4):
        """
        Args:
            sequence_length: Número de períodos históricos a usar para predecir
            horizonte_prediccion: Número de períodos futuros a predecir
        """
        self.sequence_length = sequence_length
        self.horizonte_prediccion = horizonte_prediccion
        self.scaler = MinMaxScaler()
        self.model = None
        self.feature_names = []
        self.entrenado = False
    
    def preparar_secuencias(self, data, target_col):
        """
        Prepara secuencias de datos para LSTM
        
        Args:
            data: DataFrame con series temporales
            target_col: Columna objetivo a predecir
        
        Returns:
            X, y: Arrays de secuencias de entrada y salida
        """
        # Seleccionar características relevantes
        feature_cols = [col for col in data.columns if col not in ['fecha', 'periodo']]
        self.feature_names = feature_cols
        
        # Normalizar datos
        scaled_data = self.scaler.fit_transform(data[feature_cols])
        
        X, y = [], []
        
        # Crear secuencias
        for i in range(len(scaled_data) - self.sequence_length - self.horizonte_prediccion + 1):
            # Secuencia de entrada (últimos N períodos)
            X.append(scaled_data[i:i + self.sequence_length])
            
            # Valor objetivo (próximos M períodos)
            target_idx = feature_cols.index(target_col)
            y.append(scaled_data[i + self.sequence_length:i + self.sequence_length + self.horizonte_prediccion, target_idx])
        
        return np.array(X), np.array(y)
    
    def construir_modelo(self, input_shape):
        """Construye la arquitectura del modelo LSTM"""
        if not TENSORFLOW_AVAILABLE:
            return None
        
        model = Sequential([
            LSTM(64, activation='relu', return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(32, activation='relu', return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(self.horizonte_prediccion)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def entrenar(self, data, target_col='clima_escolar', epochs=50, validation_split=0.2):
        """
        Entrena el modelo LSTM
        
        Args:
            data: DataFrame con series temporales
            target_col: Columna objetivo a predecir
            epochs: Número de épocas de entrenamiento
            validation_split: Proporción de datos para validación
        
        Returns:
            dict con métricas de entrenamiento
        """
        if not TENSORFLOW_AVAILABLE:
            return {
                'exito': False,
                'mensaje': 'TensorFlow no está disponible. Usando predicción simplificada.'
            }
        
        try:
            # Preparar datos
            X, y = self.preparar_secuencias(data, target_col)
            
            if len(X) < 10:
                return {
                    'exito': False,
                    'mensaje': f'Datos insuficientes. Se necesitan al menos {self.sequence_length + self.horizonte_prediccion + 10} registros temporales.'
                }
            
            # Dividir en entrenamiento y validación
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split, shuffle=False)
            
            # Construir modelo
            self.model = self.construir_modelo(input_shape=(X.shape[1], X.shape[2]))
            
            # Callbacks
            early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
            
            # Entrenar
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=16,
                validation_data=(X_val, y_val),
                callbacks=[early_stop],
                verbose=0
            )
            
            self.entrenado = True
            
            # Evaluar
            train_loss, train_mae = self.model.evaluate(X_train, y_train, verbose=0)
            val_loss, val_mae = self.model.evaluate(X_val, y_val, verbose=0)
            
            return {
                'exito': True,
                'train_loss': float(train_loss),
                'train_mae': float(train_mae),
                'val_loss': float(val_loss),
                'val_mae': float(val_mae),
                'epochs_trained': len(history.history['loss']),
                'target_col': target_col
            }
        
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al entrenar modelo: {str(e)}'
            }
    
    def predecir(self, data_reciente, target_col='clima_escolar', calcular_intervalos=True):
        """
        Realiza predicciones para los próximos períodos
        
        Args:
            data_reciente: DataFrame con los últimos períodos (mínimo sequence_length)
            target_col: Columna objetivo a predecir
            calcular_intervalos: Si True, calcula intervalos de confianza
        
        Returns:
            dict con predicciones e intervalos de confianza
        """
        if not self.entrenado and TENSORFLOW_AVAILABLE:
            return {
                'exito': False,
                'mensaje': 'El modelo no ha sido entrenado. Llame a entrenar() primero.'
            }
        
        try:
            # Tomar los últimos sequence_length períodos
            data_input = data_reciente.tail(self.sequence_length)
            
            # Normalizar
            feature_cols = [col for col in data_input.columns if col not in ['fecha', 'periodo']]
            scaled_input = self.scaler.transform(data_input[feature_cols])
            
            # Reshape para LSTM
            X_pred = scaled_input.reshape(1, self.sequence_length, len(feature_cols))
            
            if TENSORFLOW_AVAILABLE and self.model is not None:
                # Predicción con modelo LSTM
                prediccion_scaled = self.model.predict(X_pred, verbose=0)[0]
                
                # Desnormalizar
                target_idx = feature_cols.index(target_col)
                dummy = np.zeros((self.horizonte_prediccion, len(feature_cols)))
                dummy[:, target_idx] = prediccion_scaled
                prediccion_original = self.scaler.inverse_transform(dummy)[:, target_idx]
                
                # Calcular intervalos de confianza (simulado con múltiples predicciones)
                if calcular_intervalos:
                    predicciones_multiples = []
                    for _ in range(30):
                        pred = self.model.predict(X_pred, verbose=0)[0]
                        dummy = np.zeros((self.horizonte_prediccion, len(feature_cols)))
                        dummy[:, target_idx] = pred
                        pred_original = self.scaler.inverse_transform(dummy)[:, target_idx]
                        predicciones_multiples.append(pred_original)
                    
                    predicciones_multiples = np.array(predicciones_multiples)
                    intervalo_inf = np.percentile(predicciones_multiples, 10, axis=0)
                    intervalo_sup = np.percentile(predicciones_multiples, 90, axis=0)
                else:
                    intervalo_inf = prediccion_original * 0.9
                    intervalo_sup = prediccion_original * 1.1
            
            else:
                # Predicción simplificada (promedio móvil con tendencia)
                valores_recientes = data_input[target_col].values
                tendencia = (valores_recientes[-1] - valores_recientes[0]) / len(valores_recientes)
                
                prediccion_original = []
                for i in range(1, self.horizonte_prediccion + 1):
                    pred = valores_recientes[-1] + (tendencia * i)
                    prediccion_original.append(pred)
                
                prediccion_original = np.array(prediccion_original)
                intervalo_inf = prediccion_original * 0.85
                intervalo_sup = prediccion_original * 1.15
            
            return {
                'exito': True,
                'predicciones': prediccion_original.tolist(),
                'intervalo_confianza_inferior': intervalo_inf.tolist(),
                'intervalo_confianza_superior': intervalo_sup.tolist(),
                'horizonte_semanas': self.horizonte_prediccion,
                'target_col': target_col,
                'modelo': 'LSTM' if TENSORFLOW_AVAILABLE else 'Promedio Móvil'
            }
        
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al predecir: {str(e)}'
            }
    
    def analizar_tendencia(self, predicciones):
        """
        Analiza la tendencia de las predicciones
        
        Returns:
            dict con análisis de tendencia
        """
        if len(predicciones) < 2:
            return {'tendencia': 'insuficiente_datos'}
        
        # Calcular pendiente
        x = np.arange(len(predicciones))
        y = np.array(predicciones)
        pendiente = np.polyfit(x, y, 1)[0]
        
        # Clasificar tendencia
        if abs(pendiente) < 0.1:
            tendencia = 'estable'
        elif pendiente > 0:
            if pendiente > 0.5:
                tendencia = 'mejora_significativa'
            else:
                tendencia = 'mejora_leve'
        else:
            if pendiente < -0.5:
                tendencia = 'deterioro_significativo'
            else:
                tendencia = 'deterioro_leve'
        
        # Calcular variabilidad
        variabilidad = np.std(predicciones)
        
        return {
            'tendencia': tendencia,
            'pendiente': float(pendiente),
            'variabilidad': float(variabilidad),
            'valor_inicial': float(predicciones[0]),
            'valor_final': float(predicciones[-1]),
            'cambio_total': float(predicciones[-1] - predicciones[0])
        }


def predecir_riesgo_curso(db_manager, curso_id, horizonte_semanas=4):
    """
    Función de alto nivel para predecir el riesgo de un curso
    
    Args:
        db_manager: Instancia de DatabaseManager
        curso_id: ID del curso a analizar
        horizonte_semanas: Número de semanas a predecir
    
    Returns:
        dict con predicciones y análisis
    """
    # Obtener datos históricos
    data = db_manager.obtener_series_temporales_curso(curso_id)
    
    if len(data) < 8:
        return {
            'exito': False,
            'mensaje': f'Datos insuficientes para el curso {curso_id}. Se necesitan al menos 8 registros temporales.'
        }
    
    # Crear y entrenar modelo
    modelo = ModeloLSTMPredictor(sequence_length=4, horizonte_prediccion=horizonte_semanas)
    
    # Entrenar para clima escolar
    resultado_entrenamiento = modelo.entrenar(data, target_col='clima_escolar', epochs=50)
    
    if not resultado_entrenamiento['exito']:
        return resultado_entrenamiento
    
    # Realizar predicción
    prediccion = modelo.predecir(data, target_col='clima_escolar')
    
    if not prediccion['exito']:
        return prediccion
    
    # Analizar tendencia
    analisis_tendencia = modelo.analizar_tendencia(prediccion['predicciones'])
    
    # Guardar predicciones en BD
    for i, (pred, inf, sup) in enumerate(zip(
        prediccion['predicciones'],
        prediccion['intervalo_confianza_inferior'],
        prediccion['intervalo_confianza_superior']
    )):
        db_manager.guardar_prediccion(
            curso_id=curso_id,
            tipo_prediccion='clima_escolar',
            horizonte_semanas=i+1,
            valor_predicho=pred,
            intervalo_inf=inf,
            intervalo_sup=sup,
            modelo=prediccion['modelo']
        )
    
    # Generar alertas si es necesario
    if analisis_tendencia['tendencia'] in ['deterioro_significativo', 'deterioro_leve']:
        nivel_prioridad = 'alta' if analisis_tendencia['tendencia'] == 'deterioro_significativo' else 'media'
        
        mensaje = f"Se predice un deterioro del clima escolar en el curso {curso_id} en las próximas {horizonte_semanas} semanas."
        recomendacion = "Se recomienda implementar intervenciones preventivas de convivencia escolar."
        
        db_manager.crear_alerta(
            tipo_alerta='predictiva',
            nivel_prioridad=nivel_prioridad,
            mensaje=mensaje,
            recomendacion=recomendacion,
            curso_id=curso_id
        )
    
    return {
        'exito': True,
        'curso_id': curso_id,
        'predicciones': prediccion,
        'analisis_tendencia': analisis_tendencia,
        'metricas_entrenamiento': resultado_entrenamiento,
        'datos_historicos': len(data)
    }


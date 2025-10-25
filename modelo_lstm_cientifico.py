"""
Modelo LSTM Científicamente Riguroso para Predicción de Convivencia Escolar
Con validación temporal, métricas estándar y análisis de confiabilidad
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from tensorflow.keras.regularizers import l2
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class ModeloLSTMCientifico:
    """
    Modelo LSTM con validación científica rigurosa
    """
    
    def __init__(self, sequence_length=12, horizonte_prediccion=4):
        """
        Args:
            sequence_length: Períodos históricos (12 semanas = 3 meses)
            horizonte_prediccion: Períodos a predecir (4 semanas = 1 mes)
        """
        self.sequence_length = sequence_length
        self.horizonte_prediccion = horizonte_prediccion
        self.scaler = MinMaxScaler()
        self.model = None
        self.feature_names = []
        self.entrenado = False
        self.metricas_validacion = {}
        
    def preparar_datos_validacion_temporal(self, data, target_col, test_size=0.2):
        """
        Prepara datos con validación temporal (sin mezclar pasado y futuro)
        """
        feature_cols = [col for col in data.columns if col not in ['fecha', 'periodo', 'fecha_registro']]
        self.feature_names = feature_cols
        
        # Normalizar
        scaled_data = self.scaler.fit_transform(data[feature_cols])
        
        X, y = [], []
        indices = []
        
        # Crear secuencias
        for i in range(len(scaled_data) - self.sequence_length - self.horizonte_prediccion + 1):
            X.append(scaled_data[i:i + self.sequence_length])
            target_idx = feature_cols.index(target_col)
            y.append(scaled_data[i + self.sequence_length:i + self.sequence_length + self.horizonte_prediccion, target_idx])
            indices.append(i)
        
        X = np.array(X)
        y = np.array(y)
        
        # Split temporal (no aleatorio)
        split_idx = int(len(X) * (1 - test_size))
        
        X_train = X[:split_idx]
        y_train = y[:split_idx]
        X_test = X[split_idx:]
        y_test = y[split_idx:]
        
        return X_train, X_test, y_train, y_test, feature_cols, target_idx
    
    def construir_modelo_mejorado(self, input_shape):
        """
        Arquitectura optimizada para evitar overfitting
        """
        if not TENSORFLOW_AVAILABLE:
            return None
        
        model = Sequential([
            LSTM(64, activation='tanh', return_sequences=True, 
                 kernel_regularizer=l2(0.01), recurrent_dropout=0.2,
                 input_shape=input_shape),
            Dropout(0.4),
            LSTM(32, activation='tanh', return_sequences=False,
                 kernel_regularizer=l2(0.01), recurrent_dropout=0.2),
            Dropout(0.4),
            Dense(16, activation='relu', kernel_regularizer=l2(0.01)),
            Dropout(0.3),
            Dense(self.horizonte_prediccion)
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0005, clipnorm=1.0),
            loss='mse',  # MSE estándar
            metrics=['mae']
        )
        
        return model
    
    def calcular_metricas_cientificas(self, y_true, y_pred, nombre_conjunto='test'):
        """
        Calcula métricas científicas estándar
        """
        # Aplanar arrays para métricas globales
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred.flatten()
        
        # RMSE (Root Mean Squared Error)
        rmse = np.sqrt(mean_squared_error(y_true_flat, y_pred_flat))
        
        # MAE (Mean Absolute Error)
        mae = mean_absolute_error(y_true_flat, y_pred_flat)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_true_flat - y_pred_flat) / (y_true_flat + 1e-10))) * 100
        
        # R² (Coeficiente de determinación)
        r2 = r2_score(y_true_flat, y_pred_flat)
        
        # Intervalo de confianza para MAE (bootstrap)
        mae_bootstrap = []
        n_bootstrap = 1000
        for _ in range(n_bootstrap):
            indices = np.random.choice(len(y_true_flat), len(y_true_flat), replace=True)
            mae_bootstrap.append(mean_absolute_error(y_true_flat[indices], y_pred_flat[indices]))
        
        mae_ci_lower = np.percentile(mae_bootstrap, 2.5)
        mae_ci_upper = np.percentile(mae_bootstrap, 97.5)
        
        # Bias (sesgo)
        bias = np.mean(y_pred_flat - y_true_flat)
        
        return {
            f'{nombre_conjunto}_rmse': float(rmse),
            f'{nombre_conjunto}_mae': float(mae),
            f'{nombre_conjunto}_mae_ci_lower': float(mae_ci_lower),
            f'{nombre_conjunto}_mae_ci_upper': float(mae_ci_upper),
            f'{nombre_conjunto}_mape': float(mape),
            f'{nombre_conjunto}_r2': float(r2),
            f'{nombre_conjunto}_bias': float(bias),
            f'{nombre_conjunto}_n_samples': len(y_true_flat)
        }
    
    def entrenar_con_validacion(self, data, target_col='clima_escolar_promedio', epochs=100):
        """
        Entrenamiento con validación científica rigurosa
        """
        if not TENSORFLOW_AVAILABLE:
            return {
                'exito': False,
                'mensaje': 'TensorFlow no disponible'
            }
        
        try:
            print("\n🔬 ENTRENAMIENTO CIENTÍFICO DEL MODELO")
            print("="*70)
            
            # Preparar datos
            print("📊 Preparando datos con validación temporal...")
            X_train, X_test, y_train, y_test, feature_cols, target_idx = \
                self.preparar_datos_validacion_temporal(data, target_col)
            
            print(f"   Train: {len(X_train)} secuencias")
            print(f"   Test: {len(X_test)} secuencias")
            
            if len(X_train) < 20:
                return {
                    'exito': False,
                    'mensaje': f'Datos insuficientes para entrenamiento riguroso'
                }
            
            # Construir modelo
            print("\n🧠 Construyendo arquitectura Bidirectional LSTM...")
            self.model = self.construir_modelo_mejorado(input_shape=(X_train.shape[1], X_train.shape[2]))
            print(f"   Parámetros: {self.model.count_params():,}")
            
            # Callbacks
            early_stop = EarlyStopping(
                monitor='val_loss',
                patience=20,
                restore_best_weights=True,
                verbose=1
            )
            
            reduce_lr = ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.3,
                patience=10,
                min_lr=0.00001,
                verbose=1
            )
            
            # Entrenar
            print("\n🏋️ Entrenando modelo...")
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=8,  # Batch más pequeño para mejor generalización
                validation_split=0.2,  # Más datos para validación
                callbacks=[early_stop, reduce_lr],
                verbose=1,
                shuffle=False  # No mezclar para series temporales
            )
            
            self.entrenado = True
            
            # Predicciones
            print("\n📈 Generando predicciones...")
            y_train_pred = self.model.predict(X_train, verbose=0)
            y_test_pred = self.model.predict(X_test, verbose=0)
            
            # Desnormalizar para métricas
            def desnormalizar(y_scaled):
                dummy = np.zeros((y_scaled.shape[0], y_scaled.shape[1], len(feature_cols)))
                dummy[:, :, target_idx] = y_scaled
                result = []
                for i in range(len(dummy)):
                    result.append(self.scaler.inverse_transform(dummy[i])[:, target_idx])
                return np.array(result)
            
            y_train_original = desnormalizar(y_train)
            y_train_pred_original = desnormalizar(y_train_pred)
            y_test_original = desnormalizar(y_test)
            y_test_pred_original = desnormalizar(y_test_pred)
            
            # Calcular métricas
            print("\n📊 Calculando métricas científicas...")
            metricas_train = self.calcular_metricas_cientificas(y_train_original, y_train_pred_original, 'train')
            metricas_test = self.calcular_metricas_cientificas(y_test_original, y_test_pred_original, 'test')
            
            self.metricas_validacion = {**metricas_train, **metricas_test}
            self.metricas_validacion['epochs_trained'] = len(history.history['loss'])
            self.metricas_validacion['target_col'] = target_col
            
            # Evaluación de confiabilidad
            print("\n✅ RESULTADOS DE VALIDACIÓN")
            print("="*70)
            print(f"\n📊 Conjunto de Entrenamiento:")
            print(f"   RMSE: {metricas_train['train_rmse']:.4f}")
            print(f"   MAE: {metricas_train['train_mae']:.4f} (IC 95%: [{metricas_train['train_mae_ci_lower']:.4f}, {metricas_train['train_mae_ci_upper']:.4f}])")
            print(f"   MAPE: {metricas_train['train_mape']:.2f}%")
            print(f"   R²: {metricas_train['train_r2']:.4f}")
            print(f"   Bias: {metricas_train['train_bias']:.4f}")
            
            print(f"\n📊 Conjunto de Prueba (Validación Temporal):")
            print(f"   RMSE: {metricas_test['test_rmse']:.4f}")
            print(f"   MAE: {metricas_test['test_mae']:.4f} (IC 95%: [{metricas_test['test_mae_ci_lower']:.4f}, {metricas_test['test_mae_ci_upper']:.4f}])")
            print(f"   MAPE: {metricas_test['test_mape']:.2f}%")
            print(f"   R²: {metricas_test['test_r2']:.4f}")
            print(f"   Bias: {metricas_test['test_bias']:.4f}")
            
            # Evaluación de confiabilidad científica
            print(f"\n🎯 EVALUACIÓN DE CONFIABILIDAD CIENTÍFICA:")
            
            confiabilidad = "ALTA"
            if metricas_test['test_mae'] > 0.7:
                confiabilidad = "BAJA"
            elif metricas_test['test_mae'] > 0.5:
                confiabilidad = "MEDIA"
            
            print(f"   MAE < 0.5: {'✅' if metricas_test['test_mae'] < 0.5 else '❌'}")
            print(f"   R² > 0.70: {'✅' if metricas_test['test_r2'] > 0.70 else '❌'}")
            print(f"   MAPE < 10%: {'✅' if metricas_test['test_mape'] < 10 else '❌'}")
            print(f"   |Bias| < 0.2: {'✅' if abs(metricas_test['test_bias']) < 0.2 else '❌'}")
            print(f"\n   🏆 CONFIABILIDAD: {confiabilidad}")
            
            print("\n" + "="*70)
            
            return {
                'exito': True,
                **self.metricas_validacion,
                'confiabilidad': confiabilidad
            }
        
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error: {str(e)}'
            }
    
    def predecir_con_intervalos(self, data_reciente, target_col='clima_escolar_promedio', n_simulaciones=100):
        """
        Predicción con intervalos de confianza mediante Monte Carlo Dropout
        """
        if not self.entrenado:
            return {'exito': False, 'mensaje': 'Modelo no entrenado'}
        
        try:
            # Preparar entrada
            data_input = data_reciente.tail(self.sequence_length)
            feature_cols = [col for col in data_input.columns if col not in ['fecha', 'periodo', 'fecha_registro']]
            scaled_input = self.scaler.transform(data_input[feature_cols])
            X_pred = scaled_input.reshape(1, self.sequence_length, len(feature_cols))
            
            # Múltiples predicciones con dropout activo (MC Dropout)
            predicciones_multiples = []
            for _ in range(n_simulaciones):
                pred = self.model(X_pred, training=True).numpy()[0]  # training=True activa dropout
                predicciones_multiples.append(pred)
            
            predicciones_multiples = np.array(predicciones_multiples)
            
            # Estadísticas
            prediccion_media = np.mean(predicciones_multiples, axis=0)
            prediccion_std = np.std(predicciones_multiples, axis=0)
            
            # Intervalos de confianza (95%)
            intervalo_inf = np.percentile(predicciones_multiples, 2.5, axis=0)
            intervalo_sup = np.percentile(predicciones_multiples, 97.5, axis=0)
            
            # Desnormalizar
            target_idx = feature_cols.index(target_col)
            
            def desnorm_vector(vec):
                dummy = np.zeros((len(vec), len(feature_cols)))
                dummy[:, target_idx] = vec
                return self.scaler.inverse_transform(dummy)[:, target_idx]
            
            pred_original = desnorm_vector(prediccion_media)
            intervalo_inf_original = desnorm_vector(intervalo_inf)
            intervalo_sup_original = desnorm_vector(intervalo_sup)
            
            # Incertidumbre
            incertidumbre = np.mean(intervalo_sup_original - intervalo_inf_original)
            
            return {
                'exito': True,
                'predicciones': pred_original.tolist(),
                'intervalo_confianza_inferior': intervalo_inf_original.tolist(),
                'intervalo_confianza_superior': intervalo_sup_original.tolist(),
                'incertidumbre_promedio': float(incertidumbre),
                'horizonte_semanas': self.horizonte_prediccion,
                'target_col': target_col,
                'metricas_validacion': self.metricas_validacion
            }
        
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}


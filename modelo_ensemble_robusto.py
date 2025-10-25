"""
Modelo Ensemble Robusto para Predicción de Convivencia Escolar
Combina múltiples algoritmos para máxima confiabilidad
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class ModeloEnsembleRobusto:
    """
    Ensemble de modelos optimizado para series temporales cortas
    """
    
    def __init__(self, horizonte_prediccion=4, sequence_length=8):
        self.horizonte_prediccion = horizonte_prediccion
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        
        # Modelos del ensemble
        self.modelo_gb = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            min_samples_split=5,
            min_samples_leaf=3,
            subsample=0.8,
            random_state=42
        )
        
        self.modelo_rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42
        )
        
        self.entrenado = False
        self.metricas = {}
        
    def crear_features_temporales(self, serie):
        """
        Crea features ingenierizadas para capturar patrones temporales
        """
        features = []
        
        # Features básicas
        features.append(np.mean(serie))  # Media
        features.append(np.std(serie))   # Desviación estándar
        features.append(serie[-1])       # Último valor
        features.append(serie[0])        # Primer valor
        
        # Tendencia (regresión lineal)
        x = np.arange(len(serie))
        slope, intercept = np.polyfit(x, serie, 1)
        features.append(slope)
        features.append(intercept)
        
        # Diferencias
        if len(serie) > 1:
            features.append(serie[-1] - serie[-2])  # Diferencia última
            features.append(np.mean(np.diff(serie)))  # Diferencia promedio
        else:
            features.append(0)
            features.append(0)
        
        # Valores recientes ponderados
        pesos = np.exp(np.linspace(-1, 0, len(serie)))
        pesos = pesos / pesos.sum()
        features.append(np.sum(serie * pesos))
        
        # Percentiles
        features.append(np.percentile(serie, 25))
        features.append(np.percentile(serie, 75))
        
        # Autocorrelación (lag-1)
        if len(serie) > 2:
            autocorr = np.corrcoef(serie[:-1], serie[1:])[0, 1]
            features.append(autocorr if not np.isnan(autocorr) else 0)
        else:
            features.append(0)
        
        return features
    
    def preparar_datos(self, data, target_col):
        """
        Prepara datos con features ingenierizadas
        """
        valores = data[target_col].values
        
        X, y = [], []
        
        for i in range(len(valores) - self.sequence_length - self.horizonte_prediccion + 1):
            # Ventana histórica
            ventana = valores[i:i + self.sequence_length]
            
            # Features
            features = self.crear_features_temporales(ventana)
            X.append(features)
            
            # Target (siguiente valor - predicción 1 paso)
            y.append(valores[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def entrenar_con_validacion(self, data, target_col='clima_escolar_promedio'):
        """
        Entrena el ensemble con validación temporal
        """
        print("\n🔬 ENTRENAMIENTO ENSEMBLE ROBUSTO")
        print("="*70)
        
        # Preparar datos
        print("📊 Preparando features ingenierizadas...")
        X, y = self.preparar_datos(data, target_col)
        
        print(f"   Samples: {len(X)}")
        print(f"   Features por sample: {X.shape[1]}")
        
        if len(X) < 20:
            return {
                'exito': False,
                'mensaje': 'Datos insuficientes'
            }
        
        # Split temporal
        split_idx = int(len(X) * 0.75)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"   Train: {len(X_train)}, Test: {len(X_test)}")
        
        # Normalizar
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelos
        print("\n🏋️ Entrenando Gradient Boosting...")
        self.modelo_gb.fit(X_train_scaled, y_train)
        
        print("🏋️ Entrenando Random Forest...")
        self.modelo_rf.fit(X_train_scaled, y_train)
        
        self.entrenado = True
        
        # Predicciones
        print("\n📈 Generando predicciones...")
        y_train_pred_gb = self.modelo_gb.predict(X_train_scaled)
        y_train_pred_rf = self.modelo_rf.predict(X_train_scaled)
        y_train_pred = (y_train_pred_gb + y_train_pred_rf) / 2  # Ensemble
        
        y_test_pred_gb = self.modelo_gb.predict(X_test_scaled)
        y_test_pred_rf = self.modelo_rf.predict(X_test_scaled)
        y_test_pred = (y_test_pred_gb + y_test_pred_rf) / 2  # Ensemble
        
        # Métricas
        print("\n📊 Calculando métricas...")
        
        def calcular_metricas(y_true, y_pred, nombre):
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100
            r2 = r2_score(y_true, y_pred)
            bias = np.mean(y_pred - y_true)
            
            # Intervalo de confianza para MAE (bootstrap)
            mae_bootstrap = []
            for _ in range(1000):
                indices = np.random.choice(len(y_true), len(y_true), replace=True)
                mae_bootstrap.append(mean_absolute_error(y_true[indices], y_pred[indices]))
            
            mae_ci_lower = np.percentile(mae_bootstrap, 2.5)
            mae_ci_upper = np.percentile(mae_bootstrap, 97.5)
            
            return {
                f'{nombre}_rmse': float(rmse),
                f'{nombre}_mae': float(mae),
                f'{nombre}_mae_ci_lower': float(mae_ci_lower),
                f'{nombre}_mae_ci_upper': float(mae_ci_upper),
                f'{nombre}_mape': float(mape),
                f'{nombre}_r2': float(r2),
                f'{nombre}_bias': float(bias)
            }
        
        metricas_train = calcular_metricas(y_train, y_train_pred, 'train')
        metricas_test = calcular_metricas(y_test, y_test_pred, 'test')
        
        self.metricas = {**metricas_train, **metricas_test, 'target_col': target_col}
        
        # Resultados
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
        
        # Evaluación de confiabilidad
        print(f"\n🎯 EVALUACIÓN DE CONFIABILIDAD CIENTÍFICA:")
        
        confiabilidad = "ALTA"
        if metricas_test['test_mae'] > 0.7:
            confiabilidad = "BAJA"
        elif metricas_test['test_mae'] > 0.5:
            confiabilidad = "MEDIA"
        
        if metricas_test['test_r2'] < 0.5:
            confiabilidad = "MEDIA" if confiabilidad == "ALTA" else "BAJA"
        
        print(f"   MAE < 0.5: {'✅' if metricas_test['test_mae'] < 0.5 else '❌'}")
        print(f"   R² > 0.50: {'✅' if metricas_test['test_r2'] > 0.50 else '❌'}")
        print(f"   MAPE < 10%: {'✅' if metricas_test['test_mape'] < 10 else '❌'}")
        print(f"   |Bias| < 0.3: {'✅' if abs(metricas_test['test_bias']) < 0.3 else '❌'}")
        print(f"\n   🏆 CONFIABILIDAD: {confiabilidad}")
        
        print("\n" + "="*70)
        
        return {
            'exito': True,
            **self.metricas,
            'confiabilidad': confiabilidad
        }
    
    def predecir_multiples_pasos(self, data_reciente, target_col='clima_escolar_promedio'):
        """
        Predicción iterativa de múltiples pasos hacia adelante
        """
        if not self.entrenado:
            return {'exito': False, 'mensaje': 'Modelo no entrenado'}
        
        try:
            valores = data_reciente[target_col].values
            predicciones = []
            intervalos_inf = []
            intervalos_sup = []
            
            # Predicción iterativa
            valores_extendidos = list(valores[-self.sequence_length:])
            
            for paso in range(self.horizonte_prediccion):
                # Crear features de la ventana actual
                ventana = valores_extendidos[-self.sequence_length:]
                features = self.crear_features_temporales(ventana)
                features_scaled = self.scaler.transform([features])
                
                # Predicción ensemble
                pred_gb = self.modelo_gb.predict(features_scaled)[0]
                pred_rf = self.modelo_rf.predict(features_scaled)[0]
                pred = (pred_gb + pred_rf) / 2
                
                # Intervalo de confianza (basado en dispersión de modelos + incertidumbre)
                dispersión = abs(pred_gb - pred_rf)
                incertidumbre_base = self.metricas.get('test_mae', 0.5)
                incertidumbre_total = incertidumbre_base + (dispersión * 0.5) + (paso * 0.1)  # Aumenta con horizonte
                
                pred_inf = pred - 1.96 * incertidumbre_total
                pred_sup = pred + 1.96 * incertidumbre_total
                
                predicciones.append(pred)
                intervalos_inf.append(pred_inf)
                intervalos_sup.append(pred_sup)
                
                # Agregar predicción para próxima iteración
                valores_extendidos.append(pred)
            
            return {
                'exito': True,
                'predicciones': predicciones,
                'intervalo_confianza_inferior': intervalos_inf,
                'intervalo_confianza_superior': intervalos_sup,
                'incertidumbre_promedio': float(np.mean([intervalos_sup[i] - intervalos_inf[i] for i in range(len(intervalos_sup))])),
                'horizonte_semanas': self.horizonte_prediccion,
                'target_col': target_col,
                'metricas_validacion': self.metricas
            }
        
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}


if __name__ == "__main__":
    # Test
    import sqlite3
    
    conn = sqlite3.connect('convivir_v4.db')
    query = """
        SELECT fecha_registro, clima_escolar_promedio
        FROM cursos_temporal
        WHERE curso_id = '1°A'
        ORDER BY fecha_registro
    """
    data = pd.read_sql_query(query, conn)
    conn.close()
    
    modelo = ModeloEnsembleRobusto(horizonte_prediccion=4, sequence_length=8)
    resultados = modelo.entrenar_con_validacion(data)
    
    if resultados['exito']:
        print(f"\n✅ Confiabilidad: {resultados['confiabilidad']}")
        
        # Predicción
        pred_result = modelo.predecir_multiples_pasos(data)
        if pred_result['exito']:
            print(f"\n🔮 Predicciones: {[round(p, 2) for p in pred_result['predicciones']]}")


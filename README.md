# CONVIVIR v4.0 - Plataforma Evolucionada

## 🎓 Descripción

CONVIVIR v4.0 es una plataforma de innovación tecnológica avanzada para la prevención y gestión de la violencia escolar. Esta versión evolucionada integra modelos de Machine Learning y Deep Learning de vanguardia para transformar el análisis de convivencia escolar de **descriptivo a predictivo y prescriptivo**.

## ✨ Nuevas Funcionalidades Implementadas

### 1. **Modelo LSTM para Predicción de Series Temporales** 🤖
- Redes neuronales recurrentes (LSTM) que predicen la evolución futura de indicadores de convivencia
- Horizonte de predicción: 4-12 semanas
- Intervalos de confianza para cada predicción
- Análisis automático de tendencias (mejora, deterioro, estable)
- **Archivo**: `modelo_lstm.py`

### 2. **NLP Avanzado con Transformers** 💬
- Análisis de sentimientos con modelos transformer pre-entrenados en español (BETO)
- Extracción automática de temas principales
- Identificación de estudiantes en riesgo basándose en comentarios negativos recurrentes
- Confianza de predicción para cada análisis
- **Archivo**: `modelo_nlp.py`

### 3. **Graph Neural Networks para Análisis de Redes Sociales** 🕸️
- Construcción de grafos de interacciones sociales
- Detección de comunidades y grupos
- Identificación de estudiantes aislados
- Análisis de patrones de bullying
- Cálculo de métricas de centralidad (PageRank, betweenness, closeness)
- **Archivo**: `modelo_gnn.py`

### 4. **Sistema de Alertas Inteligentes** 🚨
- Alertas predictivas basadas en modelos LSTM
- Alertas de sentimiento basadas en análisis NLP
- Alertas sociales basadas en análisis de redes
- Priorización automática (baja, media, alta, crítica)
- Recomendaciones específicas para cada alerta

### 5. **Simulador de Intervenciones** 🎯
- Simulación "what-if" para evaluar impacto de intervenciones
- Comparación de escenarios con y sin intervención
- Visualización de mejoras esperadas
- Soporte para múltiples tipos de intervención

### 6. **Base de Datos SQLite Robusta** 💾
- Esquema normalizado con 10 tablas
- Persistencia de datos históricos
- Almacenamiento de predicciones y alertas
- ORM con SQLAlchemy
- **Archivo**: `database.py`

### 7. **Soporte para Formato Excel Mejorado** 📊
- Compatibilidad con formato de 8 hojas
- Validación automática de esquema
- Retrocompatibilidad con formato antiguo (2 hojas)
- Carga automática a base de datos

## 📁 Estructura del Proyecto

```
convivir_v4_evolucionado/
├── app.py                      # Aplicación Flask principal
├── database.py                 # Gestor de base de datos SQLite
├── modelo_lstm.py              # Modelo LSTM para predicción temporal
├── modelo_nlp.py               # Análisis NLP con transformers
├── modelo_gnn.py               # Análisis de redes sociales
├── templates/
│   ├── index.html              # Página principal
│   ├── cargar_datos.html       # Interfaz de carga de datos
│   ├── dashboard.html          # Dashboard principal
│   ├── alertas.html            # Página de alertas
│   ├── simulador.html          # Simulador de intervenciones
│   └── red_social.html         # Visualización de red social
├── uploads/                    # Carpeta para archivos cargados
├── static/                     # Archivos estáticos (CSS, JS, imágenes)
├── convivir_v4.db             # Base de datos SQLite
└── README.md                   # Este archivo
```

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación de Dependencias

```bash
pip install flask pandas numpy scikit-learn tensorflow transformers networkx sqlalchemy plotly openpyxl
```

### Iniciar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 📖 Guía de Uso

### Paso 1: Cargar Datos

1. Accede a la página principal
2. Haz clic en "📁 Cargar Datos"
3. Selecciona o arrastra tu archivo Excel
4. Espera a que se complete la carga

**Formato de Archivo Requerido:**

El archivo Excel debe contener 8 hojas:

1. **Metadata_Establecimiento** - Información del colegio
2. **Cursos_Temporal** - Evolución temporal de indicadores por curso (¡CLAVE para LSTM!)
3. **Estudiantes** - Perfil demográfico de estudiantes
4. **Evaluaciones_Socioemocionales** - Evaluaciones periódicas individuales
5. **Comentarios_Estudiantes** - Comentarios con metadata (para NLP)
6. **Interacciones_Sociales** - Registro de interacciones (¡CLAVE para GNN!)
7. **Intervenciones_Aplicadas** - Talleres y actividades realizadas
8. **Docentes** - Información del cuerpo docente

**Nota**: Se incluye un archivo de ejemplo: `CONVIVIR_Formato_Mejorado_Ejemplo.xlsx`

### Paso 2: Explorar el Dashboard

El dashboard principal muestra:
- Resumen de indicadores
- Gráficos de evolución temporal
- Predicciones LSTM
- Análisis de sentimientos
- Mapa de red social

### Paso 3: Revisar Alertas

Accede a la sección de alertas para ver:
- Alertas predictivas (deterioro esperado)
- Alertas de sentimiento (estudiantes con comentarios negativos)
- Alertas sociales (estudiantes aislados, víctimas de bullying)

### Paso 4: Usar el Simulador

1. Selecciona un curso
2. Elige un tipo de intervención
3. Define el impacto esperado
4. Visualiza la comparación de escenarios

## 🔧 API Endpoints

### Análisis Predictivo
```
GET /api/analisis_predictivo/<curso_id>
```
Ejecuta predicción LSTM para un curso específico.

### Análisis de Sentimientos
```
GET /api/analisis_sentimientos
```
Analiza todos los comentarios con NLP.

### Análisis de Red Social
```
GET /api/analisis_red_social
```
Construye y analiza el grafo de interacciones sociales.

### Obtener Alertas
```
GET /api/alertas
```
Retorna todas las alertas pendientes.

### Simular Intervención
```
POST /api/simular_intervencion
Body: {
  "curso_id": "1°A",
  "tipo_intervencion": "Taller Convivencia",
  "impacto_esperado": 0.15
}
```

## 📊 Modelos de Machine Learning

### LSTM (Long Short-Term Memory)

**Arquitectura:**
- Capa LSTM 1: 64 unidades, return_sequences=True
- Dropout: 0.2
- Capa LSTM 2: 32 unidades
- Dropout: 0.2
- Capa Densa 1: 16 unidades, ReLU
- Capa Densa 2: N unidades (horizonte de predicción)

**Entrenamiento:**
- Optimizador: Adam
- Función de pérdida: MSE (Mean Squared Error)
- Métrica: MAE (Mean Absolute Error)
- Early Stopping con paciencia de 10 épocas

### NLP con Transformers

**Modelo**: `finiteautomata/beto-sentiment-analysis`
- Basado en BERT pre-entrenado en español
- Fine-tuned para análisis de sentimientos
- Clasificación: Positivo, Neutral, Negativo
- Confianza: 0-1

**Fallback**: Análisis basado en reglas con diccionarios de palabras clave

### Graph Neural Networks

**Métricas Calculadas:**
- **In-degree**: Número de interacciones recibidas
- **Out-degree**: Número de interacciones iniciadas
- **Betweenness Centrality**: Importancia como puente entre grupos
- **Closeness Centrality**: Cercanía promedio a otros nodos
- **PageRank**: Influencia en la red

**Algoritmos:**
- Detección de comunidades: Greedy Modularity
- Componentes conectados para identificar grupos aislados

## 🎯 Optimizaciones Implementadas

### 1. Arquitectura y Rendimiento

✅ **Base de Datos SQLite** (en lugar de archivos Excel en memoria)
- Persistencia de datos
- Consultas optimizadas con índices
- Esquema normalizado

✅ **Procesamiento Asíncrono Simulado**
- Uso de threading para tareas pesadas
- Respuestas rápidas al usuario
- Actualización de estado en tiempo real

### 2. Estrategia de Datos y ML/IA

✅ **Series Temporales con LSTM**
- Predicción de tendencias futuras
- Detección temprana de deterioro

✅ **Análisis de Redes con GNN**
- Visión sistémica del ecosistema social
- Detección de patrones ocultos

✅ **NLP Avanzado**
- Análisis de sentimientos con alta precisión
- Extracción automática de temas

### 3. Funcionalidades de Valor Agregado

✅ **Sistema de Alertas Tempranas**
- Notificaciones proactivas
- Priorización automática
- Recomendaciones específicas

✅ **Simulador de Intervenciones**
- Análisis "what-if"
- Comparación de escenarios
- Optimización de recursos

## 🔄 Comparación: v3.0 vs v4.0

| Característica | v3.0 | v4.0 |
|---|---|---|
| **Almacenamiento** | Excel en memoria | SQLite persistente |
| **Análisis** | Descriptivo | Predictivo + Prescriptivo |
| **ML/IA** | Random Forest básico | LSTM + Transformers + GNN |
| **Formato de Datos** | 2 hojas estáticas | 8 hojas con datos temporales |
| **Alertas** | Ninguna | Sistema inteligente con priorización |
| **Simulación** | No disponible | Simulador de intervenciones |
| **Red Social** | No analizada | Análisis completo con GNN |
| **Sentimientos** | Reglas básicas | Transformers pre-entrenados |
| **Predicción** | No disponible | 4-12 semanas con intervalos de confianza |

## 📝 Notas Importantes

### Limitaciones de la Implementación Actual

1. **Base de Datos**: Se usa SQLite en lugar de PostgreSQL + TimescaleDB por limitaciones de infraestructura. Para producción, se recomienda migrar a PostgreSQL.

2. **Procesamiento Asíncrono**: Se simula con threading. Para producción, implementar Celery + Redis.

3. **Modelos Transformer**: Requieren descarga de modelos pre-entrenados (puede tardar en primera ejecución).

4. **Escalabilidad**: Optimizado para establecimientos de hasta 1000 estudiantes. Para mayor escala, se requiere infraestructura cloud.

### Próximos Pasos Recomendados

1. **Despliegue en Cloud** (AWS/Azure/GCP)
2. **Migración a PostgreSQL + TimescaleDB**
3. **Implementación de Celery + Redis**
4. **Integración con APIs de sistemas escolares**
5. **App móvil para alertas en tiempo real**
6. **Autenticación y autorización multi-usuario**

## 🤝 Soporte

Para preguntas, problemas o sugerencias, contacta al equipo de desarrollo de CONVIVIR.

## 📄 Licencia

Copyright © 2025 CONVIVIR - Plataforma de Innovación Tecnológica para la Prevención de Violencia Escolar

---

**Versión**: 4.0 Evolucionada
**Fecha**: Octubre 2025
**Autor**: Desarrollado con asistencia de Manus AI


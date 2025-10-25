# 🚀 Inicio Rápido - CONVIVIR v4.0

## Instalación en 3 Pasos

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Nota**: La instalación puede tardar 5-10 minutos debido a TensorFlow y Transformers.

### 2. Iniciar la Aplicación

```bash
python app.py
```

Verás un mensaje como:
```
================================================================================
CONVIVIR v4.0 - Plataforma Evolucionada
================================================================================
Iniciando servidor Flask...
Acceda a la aplicación en: http://localhost:5000
================================================================================
```

### 3. Acceder a la Aplicación

Abre tu navegador y ve a: **http://localhost:5000**

## Primeros Pasos

### Cargar Datos de Ejemplo

1. En la página principal, haz clic en **"📁 Cargar Datos"**
2. Selecciona el archivo: `CONVIVIR_Formato_Mejorado_Ejemplo.xlsx`
3. Espera a que se complete la carga
4. Serás redirigido automáticamente al Dashboard

### Explorar Funcionalidades

Una vez cargados los datos, puedes:

- **📊 Dashboard**: Ver resumen general y gráficos
- **🚨 Alertas**: Revisar alertas generadas automáticamente
- **🎯 Simulador**: Simular impacto de intervenciones
- **🕸️ Red Social**: Visualizar mapa de interacciones

## Ejecutar Análisis

### Análisis Predictivo (LSTM)

```bash
# Desde la interfaz web
Dashboard → Seleccionar Curso → "Ejecutar Predicción"

# O vía API
curl http://localhost:5000/api/analisis_predictivo/1°A
```

### Análisis de Sentimientos (NLP)

```bash
# Desde la interfaz web
Dashboard → "Analizar Sentimientos"

# O vía API
curl http://localhost:5000/api/analisis_sentimientos
```

### Análisis de Red Social (GNN)

```bash
# Desde la interfaz web
Red Social → "Analizar Red"

# O vía API
curl http://localhost:5000/api/analisis_red_social
```

## Solución de Problemas

### Error: "ModuleNotFoundError"

**Solución**: Instala las dependencias faltantes
```bash
pip install [nombre_del_módulo]
```

### Error: "Transformers no disponible"

**Solución**: Instala tf-keras
```bash
pip install tf-keras
```

El sistema funcionará con análisis basado en reglas como fallback.

### Error: "Datos insuficientes"

**Solución**: Asegúrate de que el archivo Excel tenga:
- Al menos 8-12 registros temporales en "Cursos_Temporal"
- Datos en todas las 8 hojas requeridas

### Puerto 5000 ocupado

**Solución**: Cambia el puerto en `app.py` (última línea):
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Cambiar a 5001
```

## Estructura de Archivos

```
convivir_v4_evolucionado/
├── app.py                              # ← EJECUTAR ESTE ARCHIVO
├── database.py
├── modelo_lstm.py
├── modelo_nlp.py
├── modelo_gnn.py
├── requirements.txt
├── README.md
├── INICIO_RAPIDO.md                    # ← ESTE ARCHIVO
├── CONVIVIR_Formato_Mejorado_Ejemplo.xlsx  # ← DATOS DE EJEMPLO
├── templates/
│   ├── index.html
│   ├── cargar_datos.html
│   └── ...
└── uploads/
```

## Próximos Pasos

1. ✅ Cargar tus propios datos (formato de 8 hojas)
2. ✅ Explorar predicciones LSTM
3. ✅ Revisar alertas generadas
4. ✅ Usar el simulador de intervenciones
5. ✅ Analizar la red social del establecimiento

## Ayuda Adicional

Consulta el **README.md** completo para:
- Descripción detallada de cada módulo
- API endpoints disponibles
- Arquitectura de los modelos ML
- Guía de desarrollo

---

**¿Listo?** Ejecuta `python app.py` y comienza a usar CONVIVIR v4.0 🎓

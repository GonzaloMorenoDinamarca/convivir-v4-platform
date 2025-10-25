# 🚀 Inicio Rápido - CONVIVIR v4.0.3 (Versión Estable)

## ✅ Esta es la Versión Correcta

**Versión:** 4.0.3  
**Estado:** ✅ Completamente funcional y probada  
**Fecha:** 17 de Octubre de 2025

---

## 📦 Instalación en 4 Pasos

### Paso 1: Descomprimir

Descomprime: `CONVIVIR_v4_WINDOWS_COMPATIBLE.zip`

### Paso 2: Instalar Dependencias

**Opción A: Automática (Windows)**
```bash
instalar_windows.bat
```

**Opción B: Manual**
```bash
pip install flask pandas openpyxl networkx sqlalchemy plotly matplotlib scikit-learn
```

### Paso 3: Ejecutar

```bash
python app.py
```

Deberías ver:
```
================================================================================
CONVIVIR v4.0 - Plataforma Evolucionada
================================================================================
Iniciando servidor Flask...
Acceda a la aplicación en: http://localhost:5000
================================================================================
```

### Paso 4: Cargar Datos

1. Abre tu navegador en: **http://localhost:5000**
2. Haz clic en **"📁 Cargar Datos"**
3. Selecciona: **CONVIVIR_Formato_Mejorado_Ejemplo.xlsx**
4. Espera a que se complete la carga
5. ¡Listo! Serás redirigido al Dashboard

---

## ✅ Verificación

Para verificar que todo está instalado correctamente:

```bash
python verificar_instalacion.py
```

Deberías ver:
```
✅ DEPENDENCIAS CRÍTICAS: TODAS INSTALADAS
   El sistema funcionará correctamente.
```

---

## 🎯 ¿Qué Puedes Hacer?

Una vez cargados los datos:

### 📊 Dashboard
- Ver resumen general del establecimiento
- Gráficos de evolución temporal
- Indicadores por curso

### 🚨 Alertas
- Alertas predictivas (deterioro esperado)
- Alertas de sentimiento (estudiantes en riesgo)
- Alertas sociales (aislamiento, bullying)

### 🎯 Simulador de Intervenciones
- Seleccionar curso
- Elegir tipo de intervención
- Ver impacto proyectado

### 🕸️ Red Social
- Mapa de interacciones
- Estudiantes aislados
- Líderes sociales
- Patrones de bullying

---

## 🔧 Solución de Problemas

### Error: "ModuleNotFoundError"

**Solución:**
```bash
pip install [nombre_del_módulo]
```

### Error: "No se puede cargar el archivo Excel"

**Solución:**
1. Elimina la base de datos anterior:
   ```bash
   del convivir_v4.db
   ```
2. Reinicia la aplicación:
   ```bash
   python app.py
   ```

### Puerto 5000 ocupado

**Solución:**
Edita `app.py` (última línea):
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Cambiar a 5001
```

---

## 📋 Archivos Importantes

```
convivir_v4_evolucionado/
├── app.py                              ← Ejecutar este archivo
├── database.py                         ← Base de datos (v4.0.3 corregida)
├── modelo_lstm.py                      ← Predicción temporal
├── modelo_nlp.py                       ← Análisis de sentimientos
├── modelo_gnn.py                       ← Análisis de redes
├── CONVIVIR_Formato_Mejorado_Ejemplo.xlsx  ← Datos de ejemplo
├── instalar_windows.bat                ← Instalador automático
├── verificar_instalacion.py            ← Verificar dependencias
└── templates/                          ← Interfaz web
```

---

## 💡 Consejos

### Primer Uso
1. Usa el archivo de ejemplo para familiarizarte
2. Explora todas las secciones del dashboard
3. Prueba el simulador de intervenciones

### Uso con Datos Reales
1. Crea tu archivo Excel siguiendo el formato de 8 hojas
2. Asegúrate de tener datos temporales (mínimo 8-12 semanas)
3. Incluye interacciones sociales para análisis GNN

### Rendimiento
- Para más de 500 estudiantes, considera usar PostgreSQL
- Los modelos LSTM requieren mínimo 8 semanas de datos
- El análisis GNN funciona mejor con 100+ interacciones

---

## 🎓 Datos de Ejemplo Incluidos

El archivo de ejemplo contiene:
- 1 Establecimiento (Liceo Ejemplo)
- 180 Estudiantes (6 cursos)
- 72 Registros temporales (12 semanas)
- 1,200 Evaluaciones socioemocionales
- 376 Comentarios
- 497 Interacciones sociales
- 45 Docentes

---

## 📞 Resumen

**Para empezar:**
```bash
python app.py
```

**Abrir navegador:**
```
http://localhost:5000
```

**Cargar datos:**
```
CONVIVIR_Formato_Mejorado_Ejemplo.xlsx
```

**¡Eso es todo!** 🎉

---

**Versión:** 4.0.3 Estable  
**Última actualización:** 17 de Octubre de 2025


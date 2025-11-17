# 🎓 CONVIVIR v4.0 - Instrucciones de Instalación Local

## 📋 Requisitos Previos

- **Python 3.11** (recomendado) o Python 3.8+
- **pip** (gestor de paquetes de Python)
- **4 GB de RAM** mínimo (8 GB recomendado para modelos AI)
- **2 GB de espacio en disco**

---

## 🚀 Instalación Paso a Paso

### **Paso 1: Descomprimir el Archivo**

1. Descomprime `CONVIVIR_v4_COMPLETO.zip` en una carpeta de tu elección
2. Abre una terminal/consola en esa carpeta

---

### **Paso 2: Crear Entorno Virtual (Recomendado)**

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### **Paso 3: Instalar Dependencias**

```bash
pip install -r requirements.txt
```

**Nota**: La instalación puede tardar 5-10 minutos debido a TensorFlow, PyTorch y Transformers.

---

### **Paso 4: Iniciar la Aplicación**

```bash
python start.py
```

**Salida esperada:**
```
================================================================================
🎓 CONVIVIR v4.0 - Plataforma Evolucionada
================================================================================
✅ Usando SQLite local: convivir_v4.db
✅ Sistema listo para usar
================================================================================
🌐 Acceda a la aplicación en: http://localhost:5000
================================================================================
```

---

### **Paso 5: Acceder a la Aplicación**

1. Abre tu navegador web
2. Ve a: **http://localhost:5000**
3. ¡Listo! La aplicación está funcionando

---

## 🗄️ Base de Datos

### **Modo Local (SQLite)**

Por defecto, la aplicación usa SQLite (`convivir_v4.db`) que ya incluye datos de ejemplo:
- 6 cohortes
- 180 estudiantes
- Datos semanales de prueba
- 376 comentarios para análisis NLP

### **Modo Producción (PostgreSQL)**

Si despliegas en Render.com, la aplicación detecta automáticamente la variable `DATABASE_URL` y usa PostgreSQL.

---

## 📚 Funcionalidades Disponibles

### ✅ **Dashboard Principal**
- Estadísticas en tiempo real
- Visualizaciones interactivas
- Alertas automáticas

### ✅ **Gestión de Estudiantes**
- Crear, editar, eliminar estudiantes
- Asignar a cohortes
- Ver historial individual

### ✅ **Gestión de Cohortes**
- Crear cohortes (grupos de estudiantes)
- Promover cursos sin perder datos históricos
- Seguimiento longitudinal de 4 años

### ✅ **Ingreso de Datos Semanales**
- Formulario completo de indicadores
- Observaciones individuales de estudiantes
- Eventos e intervenciones

### ✅ **Observaciones de Estudiantes**
- Ver todas las observaciones registradas
- Filtros por estudiante, tipo, fecha
- Estadísticas de observaciones

### ✅ **Análisis Predictivo (LSTM)**
- Predicción de clima escolar 4 semanas adelante
- Intervalos de confianza
- Análisis de tendencias

### ✅ **Análisis de Sentimientos (NLP)**
- Procesamiento de comentarios con IA
- Detección de estudiantes en riesgo
- Análisis de temas principales

### ✅ **Análisis de Red Social (GNN)**
- Visualización de interacciones sociales
- Detección de estudiantes aislados
- Métricas de centralidad

---

## 🔧 Solución de Problemas

### **Error: "No module named 'tensorflow'"**
```bash
pip install tensorflow==2.15.0
```

### **Error: "No module named 'transformers'"**
```bash
pip install transformers==4.36.2
```

### **Error: "Port 5000 already in use"**

**Windows:**
```bash
# Cambiar puerto en start.py línea 30
port = int(os.environ.get('PORT', 8080))
```

**macOS/Linux:**
```bash
# Matar proceso en puerto 5000
lsof -ti:5000 | xargs kill -9
```

### **La aplicación es muy lenta**

Los modelos de IA (TensorFlow, PyTorch) requieren recursos. Recomendaciones:
- Cerrar otras aplicaciones
- Usar al menos 8 GB de RAM
- La primera carga de modelos es más lenta

---

## 📊 Datos de Ejemplo

La base de datos incluye:

- **6 Cohortes**: Generación 2025-2028, 2026-2029, etc.
- **180 Estudiantes**: Distribuidos en 6 cursos
- **Datos Semanales**: Indicadores de clima escolar
- **376 Comentarios**: Para análisis de sentimientos
- **Interacciones Sociales**: Para análisis de redes

---

## 🔄 Actualizar la Aplicación

Si hay una nueva versión:

1. Descarga el nuevo ZIP
2. **Respalda tu base de datos**: Copia `convivir_v4.db` a un lugar seguro
3. Descomprime el nuevo ZIP
4. Reemplaza el archivo `convivir_v4.db` con tu respaldo
5. Reinstala dependencias: `pip install -r requirements.txt`

---

## 🌐 Desplegar en Producción

Para tener la aplicación disponible 24/7 en internet:

1. Sigue las instrucciones en `README.md`
2. Usa Render.com (gratis)
3. Configura PostgreSQL para persistencia de datos

---

## 📞 Soporte

Para preguntas o problemas:
- Revisa `README.md` para documentación completa
- Revisa `FUNDAMENTO_CIENTIFICO_CONVIVIR.md` para entender los modelos AI
- Revisa `DOCUMENTACION_SEGUIMIENTO_LONGITUDINAL.md` para el sistema de cohortes

---

## 🎯 Próximos Pasos

1. **Explora el Dashboard**: Ve a http://localhost:5000
2. **Ingresa Datos Semanales**: Usa el formulario de ingreso de datos
3. **Prueba el Análisis de Sentimientos**: Haz clic en el botón correspondiente
4. **Revisa las Observaciones**: Ve a la página de observaciones de estudiantes
5. **Gestiona Estudiantes**: Crea, edita o elimina estudiantes

---

**Desarrollado por Gonzalo Moreno**  
**CONVIVIR v4.0 - Plataforma de Prevención de Violencia Escolar**


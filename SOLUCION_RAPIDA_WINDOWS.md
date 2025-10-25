# 🚀 Solución Rápida para Windows - CONVIVIR v4.0

## ❌ Problema que Encontraste

Al ejecutar `pip install -r requirements.txt` obtuviste un error porque:
- Estás usando **Python 3.13** en **Windows**
- Algunas librerías (pandas, numpy) intentan compilarse desde código fuente
- Windows no tiene los compiladores de C/C++ necesarios instalados

## ✅ Solución en 3 Pasos (5 minutos)

### Paso 1: Eliminar instalaciones problemáticas

Abre **PowerShell** o **CMD** en el directorio del proyecto y ejecuta:

```bash
pip uninstall pandas numpy tensorflow transformers -y
```

### Paso 2: Instalar dependencias compatibles

```bash
pip install flask pandas openpyxl networkx sqlalchemy plotly matplotlib scikit-learn
```

**Esto instalará automáticamente las últimas versiones compatibles con Windows.**

### Paso 3: Ejecutar la aplicación

```bash
python app.py
```

Si ves este mensaje, ¡funciona!:
```
================================================================================
CONVIVIR v4.0 - Plataforma Evolucionada
================================================================================
Iniciando servidor Flask...
Acceda a la aplicación en: http://localhost:5000
================================================================================
```

Abre tu navegador en: **http://localhost:5000**

---

## 🎯 ¿Qué Funcionará?

### ✅ Funcionalidades Garantizadas (Sin TensorFlow)

- ✅ **Carga de datos Excel** (8 hojas)
- ✅ **Base de datos SQLite**
- ✅ **Análisis de redes sociales (GNN)** - Completo
- ✅ **Dashboard interactivo**
- ✅ **Sistema de alertas**
- ✅ **Visualizaciones con Plotly**
- ⚠️ **Predicción LSTM** - Versión simplificada (promedio móvil)
- ⚠️ **NLP** - Versión basada en reglas (sin transformers)

### 🔧 Funcionalidades Opcionales (Si instalas TensorFlow)

Si deseas la predicción LSTM completa, intenta instalar TensorFlow:

```bash
pip install tensorflow
```

Si funciona: ✅ Predicción LSTM completa con redes neuronales  
Si falla: ⚠️ El sistema seguirá funcionando con versión simplificada

---

## 📋 Comandos Completos (Copiar y Pegar)

```bash
# 1. Navegar al directorio del proyecto
cd convivir_v4_evolucionado

# 2. Limpiar instalaciones previas
pip uninstall pandas numpy tensorflow transformers -y

# 3. Instalar dependencias básicas (SIN ERRORES)
pip install flask pandas openpyxl networkx sqlalchemy plotly matplotlib scikit-learn

# 4. Verificar instalación
python verificar_instalacion.py

# 5. Ejecutar aplicación
python app.py
```

---

## 🔍 Verificar Instalación

Ejecuta este comando para ver qué está instalado:

```bash
python verificar_instalacion.py
```

Te mostrará:
- ✅ Módulos instalados correctamente
- ❌ Módulos faltantes (si los hay)
- 🟢 Estado general del sistema

---

## 💡 Alternativa: Usar requirements_windows.txt

En lugar de `requirements.txt`, usa el archivo compatible con Windows:

```bash
pip install -r requirements_windows.txt
```

Este archivo tiene versiones flexibles que se instalan sin problemas en Windows.

---

## 🆘 Si Aún Tienes Problemas

### Opción A: Instalación Ultra-Mínima

```bash
pip install flask pandas openpyxl networkx sqlalchemy plotly
```

Esto instalará solo lo esencial. El sistema funcionará con funcionalidades básicas.

### Opción B: Usar Anaconda (Recomendado para Windows)

1. Descargar Anaconda: https://www.anaconda.com/download
2. Instalar Anaconda
3. Abrir Anaconda Prompt
4. Ejecutar:

```bash
conda create -n convivir python=3.11
conda activate convivir
conda install flask pandas openpyxl networkx sqlalchemy plotly matplotlib scikit-learn
pip install tensorflow  # Opcional
cd convivir_v4_evolucionado
python app.py
```

Anaconda maneja mejor las dependencias en Windows.

---

## 📞 Resumen

**Problema:** Versiones específicas requieren compilación  
**Solución:** Instalar versiones flexibles sin especificar número exacto  
**Resultado:** Sistema funcional con todas las características principales  

**Comando mágico:**
```bash
pip install flask pandas openpyxl networkx sqlalchemy plotly matplotlib scikit-learn
```

¡Listo! 🎉


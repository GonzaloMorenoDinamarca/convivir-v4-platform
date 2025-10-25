# 🪟 Guía de Instalación para Windows - CONVIVIR v4.0

## ⚠️ Problema Detectado

El error que encontraste ocurre porque algunas librerías (pandas, numpy) intentan compilarse desde el código fuente y requieren compiladores de C/C++ (Visual Studio Build Tools) que no están instalados en tu sistema Windows.

## ✅ Solución Rápida (Recomendada)

### Opción 1: Instalación Simplificada (Sin compilación)

```bash
# 1. Desinstalar versiones problemáticas (si existen)
pip uninstall pandas numpy tensorflow transformers -y

# 2. Instalar versiones compatibles con Windows
pip install --upgrade pip
pip install flask pandas numpy openpyxl scikit-learn networkx sqlalchemy plotly matplotlib python-dateutil werkzeug

# 3. (OPCIONAL) Instalar TensorFlow si lo deseas
pip install tensorflow

# 4. (OPCIONAL) Instalar Transformers si lo deseas
pip install transformers
```

### Opción 2: Usar el archivo requirements_windows.txt

```bash
pip install -r requirements_windows.txt
```

## 🔧 Instalación Paso a Paso

### 1. Verificar Python

Abre PowerShell o CMD y verifica tu versión de Python:

```bash
python --version
```

Deberías ver: `Python 3.13.x` o similar.

### 2. Actualizar pip

```bash
python -m pip install --upgrade pip
```

### 3. Instalar Dependencias Básicas (Sin Errores)

```bash
pip install flask pandas numpy openpyxl scikit-learn networkx sqlalchemy plotly matplotlib
```

**Nota:** Estas versiones se instalarán automáticamente en sus últimas versiones compatibles con tu sistema.

### 4. Probar la Aplicación

```bash
cd convivir_v4_evolucionado
python app.py
```

Si ves este mensaje, ¡está funcionando!:
```
================================================================================
CONVIVIR v4.0 - Plataforma Evolucionada
================================================================================
Iniciando servidor Flask...
Acceda a la aplicación en: http://localhost:5000
================================================================================
```

## 🎯 ¿Qué Funcionalidades Estarán Disponibles?

### ✅ Sin TensorFlow ni Transformers (Instalación Básica)

El sistema funcionará con versiones simplificadas:

- ✅ **Base de datos SQLite** - Funciona 100%
- ✅ **Carga de datos Excel** - Funciona 100%
- ✅ **Análisis de redes sociales (GNN)** - Funciona 100%
- ✅ **Dashboard y visualizaciones** - Funciona 100%
- ✅ **Sistema de alertas** - Funciona 100%
- ⚠️ **Predicción LSTM** - Usará modelo simplificado (promedio móvil)
- ⚠️ **NLP Avanzado** - Usará análisis basado en reglas (sin transformers)

### ✅ Con TensorFlow (Instalación Completa)

Si instalas TensorFlow exitosamente:

```bash
pip install tensorflow
```

Tendrás acceso a:
- ✅ **Predicción LSTM completa** con redes neuronales
- ✅ Todas las demás funcionalidades

### ✅ Con Transformers (Instalación Ultra-Completa)

Si instalas Transformers exitosamente:

```bash
pip install transformers
```

Tendrás acceso a:
- ✅ **NLP Avanzado** con modelos BETO
- ✅ Análisis de sentimientos de alta precisión

## 🚨 Solución de Problemas Comunes

### Error: "Microsoft Visual C++ 14.0 is required"

**Solución 1 (Más Fácil):** Instalar versiones precompiladas

```bash
pip install --only-binary :all: pandas numpy
```

**Solución 2:** Instalar Visual Studio Build Tools (Requiere ~7GB)

1. Descargar: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Instalar "Desktop development with C++"
3. Reiniciar y volver a intentar

**Solución 3 (Recomendada):** Usar versiones más recientes que ya están precompiladas

```bash
pip install --upgrade pandas numpy
```

### Error: "No module named 'tensorflow'"

**Solución:** El sistema funcionará sin TensorFlow usando modelos simplificados. Si deseas instalarlo:

```bash
pip install tensorflow
```

Si falla, el sistema seguirá funcionando con predicciones basadas en promedio móvil.

### Error: "No module named 'transformers'"

**Solución:** El sistema funcionará sin Transformers usando análisis basado en reglas. Si deseas instalarlo:

```bash
pip install transformers
```

Si falla, el sistema seguirá funcionando con análisis de sentimientos basado en diccionarios.

## 📋 Instalación Mínima Garantizada

Si todo lo demás falla, esta instalación **garantizada** funcionará:

```bash
# Dependencias absolutamente necesarias
pip install flask
pip install pandas
pip install openpyxl
pip install networkx
pip install sqlalchemy
pip install plotly

# Ejecutar aplicación
python app.py
```

El sistema funcionará con funcionalidades básicas pero completamente operativo.

## 🔍 Verificar Instalación

Ejecuta este script para verificar qué está instalado:

```python
# verificar_instalacion.py
import sys

print("=" * 60)
print("VERIFICACIÓN DE DEPENDENCIAS - CONVIVIR v4.0")
print("=" * 60)

modulos = {
    'flask': 'Framework Web',
    'pandas': 'Análisis de Datos',
    'numpy': 'Computación Numérica',
    'openpyxl': 'Lectura de Excel',
    'sklearn': 'Machine Learning Básico',
    'networkx': 'Análisis de Redes',
    'sqlalchemy': 'Base de Datos',
    'plotly': 'Visualizaciones',
    'tensorflow': 'Deep Learning (LSTM) - OPCIONAL',
    'transformers': 'NLP Avanzado - OPCIONAL'
}

instalados = []
faltantes = []

for modulo, descripcion in modulos.items():
    try:
        __import__(modulo)
        print(f"✅ {modulo:20s} - {descripcion}")
        instalados.append(modulo)
    except ImportError:
        print(f"❌ {modulo:20s} - {descripcion}")
        faltantes.append(modulo)

print("\n" + "=" * 60)
print(f"Instalados: {len(instalados)}/{len(modulos)}")
print("=" * 60)

if 'tensorflow' not in instalados:
    print("\n⚠️  TensorFlow no instalado: Se usará modelo LSTM simplificado")

if 'transformers' not in instalados:
    print("⚠️  Transformers no instalado: Se usará NLP basado en reglas")

if len(faltantes) <= 2 and all(m in ['tensorflow', 'transformers'] for m in faltantes):
    print("\n✅ SISTEMA OPERATIVO - Listo para usar!")
else:
    print(f"\n⚠️  Instalar módulos faltantes: pip install {' '.join(faltantes)}")
```

Guarda este código como `verificar_instalacion.py` y ejecútalo:

```bash
python verificar_instalacion.py
```

## 🎯 Resumen de Comandos

```bash
# 1. Navegar al directorio
cd convivir_v4_evolucionado

# 2. Instalar dependencias básicas (SIN ERRORES)
pip install flask pandas openpyxl networkx sqlalchemy plotly

# 3. Ejecutar aplicación
python app.py

# 4. Abrir navegador
# http://localhost:5000
```

## 💡 Recomendación Final

Para Windows, la mejor opción es:

1. **Instalar solo las dependencias básicas** (sin versiones específicas)
2. **Dejar que pip instale las últimas versiones compatibles**
3. **No preocuparse por TensorFlow y Transformers** - el sistema tiene fallbacks

El sistema está diseñado para funcionar **sin necesidad de todas las librerías avanzadas**. Las funcionalidades core (base de datos, análisis de redes, alertas, simulador) funcionarán perfectamente.

---

**¿Necesitas ayuda?** Ejecuta `python verificar_instalacion.py` y comparte el resultado.


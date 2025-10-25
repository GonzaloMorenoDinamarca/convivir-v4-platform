# 🪟 LÉEME PRIMERO - Instalación en Windows

## 🎯 Has encontrado un error de instalación

El error que obtuviste es **común en Windows** y tiene una solución simple.

---

## ✅ SOLUCIÓN RÁPIDA (3 comandos)

Abre **PowerShell** o **CMD** en la carpeta `convivir_v4_evolucionado` y ejecuta:

```bash
# 1. Limpiar
pip uninstall pandas numpy tensorflow transformers -y

# 2. Instalar (sin versiones específicas)
pip install flask pandas openpyxl networkx sqlalchemy plotly matplotlib scikit-learn

# 3. Ejecutar
python app.py
```

**¡Listo!** Abre tu navegador en: http://localhost:5000

---

## 🚀 INSTALACIÓN AUTOMÁTICA (Más Fácil)

Haz doble clic en el archivo:

```
instalar_windows.bat
```

Este script instalará todo automáticamente.

---

## 📋 Archivos Importantes

- **SOLUCION_RAPIDA_WINDOWS.md** - Guía completa de solución
- **INSTALACION_WINDOWS.md** - Guía detallada paso a paso
- **instalar_windows.bat** - Instalador automático
- **verificar_instalacion.py** - Verifica qué está instalado
- **requirements_windows.txt** - Dependencias compatibles con Windows

---

## ❓ ¿Por qué ocurrió el error?

El archivo `requirements.txt` original especifica versiones exactas (ej: `pandas==2.1.4`) que requieren compilación en Windows. La solución es instalar versiones más recientes que ya vienen precompiladas.

---

## 🎯 ¿Qué funcionará después de instalar?

✅ **TODO** - Todas las funcionalidades principales:
- Carga de datos Excel
- Base de datos SQLite
- Análisis de redes sociales (GNN)
- Dashboard interactivo
- Sistema de alertas
- Visualizaciones

⚠️ **Versiones simplificadas** (si no instalas TensorFlow):
- Predicción LSTM: Usará promedio móvil en lugar de redes neuronales
- NLP: Usará análisis basado en reglas en lugar de transformers

**Nota:** El sistema está diseñado para funcionar perfectamente sin TensorFlow.

---

## 🆘 Si necesitas ayuda

1. Lee: **SOLUCION_RAPIDA_WINDOWS.md**
2. Ejecuta: `python verificar_instalacion.py`
3. Si todo falla, usa: **instalar_windows.bat**

---

**¡El sistema funcionará perfectamente en Windows!** 🎉


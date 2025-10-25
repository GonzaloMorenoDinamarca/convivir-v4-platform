@echo off
REM Script de Instalacion Automatica para Windows - CONVIVIR v4.0
REM Ejecutar como: instalar_windows.bat

echo ================================================================================
echo CONVIVIR v4.0 - Instalacion Automatica para Windows
echo ================================================================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM Actualizar pip
echo [2/5] Actualizando pip...
python -m pip install --upgrade pip --quiet
echo OK - pip actualizado
echo.

REM Desinstalar versiones problematicas
echo [3/5] Limpiando instalaciones previas...
pip uninstall pandas numpy tensorflow transformers -y >nul 2>&1
echo OK - Limpieza completada
echo.

REM Instalar dependencias basicas
echo [4/5] Instalando dependencias basicas...
echo Esto puede tardar 2-3 minutos...
pip install flask pandas openpyxl networkx sqlalchemy plotly matplotlib scikit-learn --quiet
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de dependencias
    echo Intenta manualmente: pip install flask pandas openpyxl networkx sqlalchemy plotly
    pause
    exit /b 1
)
echo OK - Dependencias basicas instaladas
echo.

REM Verificar instalacion
echo [5/5] Verificando instalacion...
python verificar_instalacion.py
echo.

echo ================================================================================
echo INSTALACION COMPLETADA
echo ================================================================================
echo.
echo Para iniciar la aplicacion, ejecuta:
echo     python app.py
echo.
echo Luego abre tu navegador en: http://localhost:5000
echo.
echo ================================================================================
pause


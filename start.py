#!/usr/bin/env python3
"""
Script de inicio para CONVIVIR v4.0
Fuerza modo producción sin reloader
"""

import os
import sys

# Forzar modo producción
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Importar la aplicación
from app import app, inicializar_datos

if __name__ == '__main__':
    print("=" * 80)
    print("🎓 CONVIVIR v4.0 - Plataforma Evolucionada")
    print("=" * 80)
    
    # Inicializar datos
    inicializar_datos()
    
    print("=" * 80)
    print("✅ Sistema listo para usar")
    print("=" * 80)
    
    # Obtener puerto
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Acceda a la aplicación en: http://localhost:{port}")
    print("=" * 80)
    
    # Iniciar servidor SIN debug y SIN reloader
    from werkzeug.serving import run_simple
    run_simple(
        '0.0.0.0',
        port,
        app,
        use_debugger=False,
        use_reloader=False,
        threaded=True
    )


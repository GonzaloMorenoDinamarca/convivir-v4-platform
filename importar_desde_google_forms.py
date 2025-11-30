#!/usr/bin/env python3
"""
Script de Importación de Google Forms a CONVIVIR v4.0 (Versión Mejorada con NLP)
Autor: Manus AI
Fecha: 30 de Noviembre, 2025

Este script lee las respuestas de un formulario de Google Forms (almacenadas en Google Sheets),
las importa a la aplicación CONVIVIR v4.0, guarda los comentarios individuales y ejecuta
análisis NLP para identificar estudiantes en riesgo.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
from datetime import datetime
import json
import sys
import os

# Agregar el directorio actual al path para importar módulos locales
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from modelo_nlp import analizar_sentimientos_establecimiento, AnalizadorNLPAvanzado

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# URL de la aplicación CONVIVIR v4.0
CONVIVIR_API_URL = "http://localhost:5000/api/ingresar_datos_semanales"

# ID de la hoja de cálculo de Google Sheets (se obtiene de la URL)
# Ejemplo: https://docs.google.com/spreadsheets/d/ABC123XYZ/edit
GOOGLE_SHEET_ID = "TU_SHEET_ID_AQUI"

# Nombre de la hoja dentro del archivo de Google Sheets
SHEET_NAME = "Respuestas de formulario 1"

# Archivo de credenciales de Google Cloud (JSON)
CREDENTIALS_FILE = "credenciales_google.json"

# Base de datos local
DATABASE_PATH = "convivir_v4.db"

# ============================================================================
# MAPEO DE COLUMNAS
# ============================================================================

# Mapeo entre las columnas del Google Sheets y los campos de la API
COLUMN_MAPPING = {
    "Marca temporal": "timestamp",
    "Dirección de correo electrónico": "email",
    "Nombre Completo": "nombre_completo",
    "Curso": "curso",
    "Me siento seguro/a en la sala de clases.": "clima_escolar",
    "Mis profesores me apoyan cuando lo necesito.": "apoyo_docentes",
    "Siento que puedo participar activamente en clases.": "participacion",
    "Generalmente, me siento bien conmigo mismo/a.": "autoestima",
    "Entiendo cómo se sienten mis compañeros.": "empatia",
    "Sé cómo resolver mis problemas con compañeros sin pelear.": "resolucion_conflictos",
    "Incidentes de bullying (burlas, exclusión, etc.)": "incidentes_bullying",
    "Incidentes de violencia física (empujones, golpes)": "incidentes_violencia",
    "Incidentes de discriminación (por origen, género, etc.)": "incidentes_discriminacion",
    "Si quieres reportar algo de forma anónima, puedes hacerlo aquí.": "comentario_texto"
}

# Mapeo de respuestas de frecuencia a números
FREQUENCY_MAPPING = {
    "Nunca": 0,
    "1-2 veces": 1,
    "3-5 veces": 3,
    "Más de 5 veces": 6
}

# ============================================================================
# FUNCIONES
# ============================================================================

def conectar_google_sheets():
    """
    Conecta con Google Sheets usando las credenciales de servicio.
    
    Returns:
        gspread.Spreadsheet: Objeto de la hoja de cálculo
    """
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    
    # Abrir la hoja de cálculo
    sheet = client.open_by_key(GOOGLE_SHEET_ID)
    worksheet = sheet.worksheet(SHEET_NAME)
    
    return worksheet


def leer_respuestas(worksheet):
    """
    Lee todas las respuestas de la hoja de cálculo.
    
    Args:
        worksheet: Objeto de la hoja de trabajo de gspread
        
    Returns:
        pandas.DataFrame: DataFrame con las respuestas
    """
    # Obtener todos los registros
    records = worksheet.get_all_records()
    
    # Convertir a DataFrame
    df = pd.DataFrame(records)
    
    return df


def buscar_estudiante_por_nombre(db, nombre_completo, curso):
    """
    Busca un estudiante en la base de datos por nombre y curso.
    
    Args:
        db: DatabaseManager
        nombre_completo: Nombre completo del estudiante
        curso: Curso del estudiante
        
    Returns:
        str: ID del estudiante o None si no se encuentra
    """
    with db.get_session() as session:
        from sqlalchemy import text
        query = text("""
            SELECT estudiante_id FROM estudiantes 
            WHERE nombre_completo LIKE :nombre AND curso_id = :curso
            LIMIT 1
        """)
        result = session.execute(query, {
            'nombre': f'%{nombre_completo}%',
            'curso': curso
        }).fetchone()
        
        if result:
            return result[0]
        return None


def guardar_comentario_individual(db, estudiante_id, comentario_texto, curso, timestamp):
    """
    Guarda un comentario individual en la base de datos.
    
    Args:
        db: DatabaseManager
        estudiante_id: ID del estudiante
        comentario_texto: Texto del comentario
        curso: Curso del estudiante
        timestamp: Marca temporal del comentario
        
    Returns:
        int: ID del comentario guardado
    """
    if not comentario_texto or len(str(comentario_texto).strip()) == 0:
        return None
    
    with db.get_session() as session:
        from sqlalchemy import text
        from database import Comentario
        
        # Crear comentario
        comentario = Comentario(
            estudiante_id=estudiante_id,
            fecha_comentario=timestamp,
            periodo=f"Semana {datetime.now().isocalendar()[1]}",
            tipo_comentario="Reporte Anónimo Google Forms",
            comentario_texto=str(comentario_texto).strip(),
            tema_principal=None,
            tono_percibido=None
        )
        
        session.add(comentario)
        session.commit()
        
        print(f"   💬 Comentario guardado para estudiante {estudiante_id}")
        return comentario.id


def transformar_datos(df, db):
    """
    Transforma los datos del DataFrame al formato requerido por la API.
    Guarda comentarios individuales en la base de datos.
    
    Args:
        df: DataFrame con las respuestas del formulario
        db: DatabaseManager para guardar comentarios
        
    Returns:
        list: Lista de diccionarios con los datos transformados
    """
    datos_transformados = []
    comentarios_guardados = 0
    
    for _, row in df.iterrows():
        # Obtener datos básicos
        curso = row.get("Curso", "Sin curso")
        nombre_completo = row.get("Nombre Completo", "Anónimo")
        timestamp = pd.to_datetime(row.get("Marca temporal", datetime.now()))
        
        # Buscar ID del estudiante
        estudiante_id = buscar_estudiante_por_nombre(db, nombre_completo, curso)
        
        if not estudiante_id:
            print(f"   ⚠️ No se encontró estudiante: {nombre_completo} ({curso})")
            # Generar ID temporal basado en timestamp
            estudiante_id = f"TEMP_{int(timestamp.timestamp())}"
        
        # Guardar comentario si existe
        comentario_texto = row.get("Si quieres reportar algo de forma anónima, puedes hacerlo aquí.", "")
        if comentario_texto and len(str(comentario_texto).strip()) > 0:
            comentario_id = guardar_comentario_individual(db, estudiante_id, comentario_texto, curso, timestamp)
            if comentario_id:
                comentarios_guardados += 1
        
        # Convertir respuestas de frecuencia a números
        incidentes_bullying = FREQUENCY_MAPPING.get(
            row.get("Incidentes de bullying (burlas, exclusión, etc.)", "Nunca"), 0
        )
        incidentes_violencia = FREQUENCY_MAPPING.get(
            row.get("Incidentes de violencia física (empujones, golpes)", "Nunca"), 0
        )
        incidentes_discriminacion = FREQUENCY_MAPPING.get(
            row.get("Incidentes de discriminación (por origen, género, etc.)", "Nunca"), 0
        )
        
        # Contar reportes anónimos
        reportes = 1 if comentario_texto and len(str(comentario_texto).strip()) > 0 else 0
        
        datos_transformados.append({
            "curso": curso,
            "clima_escolar": float(row.get("Me siento seguro/a en la sala de clases.", 5)),
            "apoyo_docentes": float(row.get("Mis profesores me apoyan cuando lo necesito.", 5)),
            "participacion": float(row.get("Siento que puedo participar activamente en clases.", 5)),
            "autoestima": float(row.get("Generalmente, me siento bien conmigo mismo/a.", 5)),
            "empatia": float(row.get("Entiendo cómo se sienten mis compañeros.", 5)),
            "resolucion_conflictos": float(row.get("Sé cómo resolver mis problemas con compañeros sin pelear.", 5)),
            "incidentes_bullying": incidentes_bullying,
            "incidentes_violencia": incidentes_violencia,
            "incidentes_discriminacion": incidentes_discriminacion,
            "reportes_anonimos": reportes
        })
    
    print(f"   ✅ {comentarios_guardados} comentarios guardados en la base de datos")
    
    return datos_transformados


def calcular_promedios_por_curso(datos):
    """
    Calcula los promedios de cada indicador por curso.
    
    Args:
        datos: Lista de diccionarios con los datos individuales
        
    Returns:
        dict: Diccionario con los promedios por curso
    """
    df = pd.DataFrame(datos)
    
    # Agrupar por curso y calcular promedios
    promedios = df.groupby('curso').agg({
        'clima_escolar': 'mean',
        'apoyo_docentes': 'mean',
        'participacion': 'mean',
        'autoestima': 'mean',
        'empatia': 'mean',
        'resolucion_conflictos': 'mean',
        'incidentes_bullying': 'sum',
        'incidentes_violencia': 'sum',
        'incidentes_discriminacion': 'sum',
        'reportes_anonimos': 'sum'
    }).reset_index()
    
    return promedios.to_dict('records')


def enviar_a_convivir(datos_curso):
    """
    Envía los datos de un curso a la API de CONVIVIR v4.0.
    
    Args:
        datos_curso: Diccionario con los datos del curso
        
    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    # Preparar payload para la API
    payload = {
        "fecha": datetime.now().strftime('%Y-%m-%d'),
        "curso": datos_curso['curso'],
        "periodo": f"Semana {datetime.now().isocalendar()[1]}",
        "clima_escolar": round(datos_curso['clima_escolar'], 2),
        "apoyo_docentes": round(datos_curso['apoyo_docentes'], 2),
        "participacion": round(datos_curso['participacion'], 2),
        "empatia": round(datos_curso['empatia'], 2),
        "autoestima": round(datos_curso['autoestima'], 2),
        "resolucion_conflictos": round(datos_curso['resolucion_conflictos'], 2),
        "incidentes_bullying": int(datos_curso['incidentes_bullying']),
        "incidentes_violencia": int(datos_curso['incidentes_violencia']),
        "incidentes_discriminacion": int(datos_curso['incidentes_discriminacion']),
        "reportes_anonimos": int(datos_curso['reportes_anonimos']),
        "asistencia": 0,  # Debe ser completado manualmente
        "promedio_notas": 0  # Debe ser completado manualmente
    }
    
    try:
        response = requests.post(
            CONVIVIR_API_URL,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('exito'):
                print(f"✅ Datos enviados exitosamente para {datos_curso['curso']}")
                return True
            else:
                print(f"❌ Error al enviar datos para {datos_curso['curso']}: {result.get('mensaje')}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code} al enviar datos para {datos_curso['curso']}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción al enviar datos para {datos_curso['curso']}: {str(e)}")
        return False


def ejecutar_analisis_nlp(db):
    """
    Ejecuta el análisis NLP sobre los comentarios guardados.
    
    Args:
        db: DatabaseManager
        
    Returns:
        dict: Resultados del análisis
    """
    print()
    print("🤖 Ejecutando análisis NLP sobre comentarios...")
    
    try:
        resultado = analizar_sentimientos_establecimiento(db)
        
        if resultado.get('exito'):
            reporte = resultado.get('reporte_general', {})
            estudiantes_riesgo = resultado.get('estudiantes_en_riesgo', [])
            
            print(f"✅ Análisis NLP completado")
            print(f"   📊 Total comentarios analizados: {reporte.get('total_comentarios', 0)}")
            print(f"   📈 Distribución: {reporte.get('distribucion_sentimientos', {})}")
            print(f"   ⚠️ Estudiantes en riesgo detectados: {len(estudiantes_riesgo)}")
            
            if estudiantes_riesgo:
                print()
                print("   🚨 ESTUDIANTES EN RIESGO:")
                for est in estudiantes_riesgo[:5]:  # Mostrar top 5
                    print(f"      - {est['estudiante_id']}: {est['comentarios_negativos']} comentarios negativos")
            
            return resultado
        else:
            print(f"⚠️ No se pudo completar el análisis NLP: {resultado.get('mensaje')}")
            return None
            
    except Exception as e:
        print(f"❌ Error al ejecutar análisis NLP: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """
    Función principal del script.
    """
    print("=" * 70)
    print("CONVIVIR v4.0 - Importación desde Google Forms (con Análisis NLP)")
    print("=" * 70)
    print()
    
    try:
        # Inicializar base de datos
        print("🗄️ Conectando con la base de datos local...")
        db = DatabaseManager(DATABASE_PATH)
        print("✅ Conectado a la base de datos")
        print()
        
        # 1. Conectar con Google Sheets
        print("📊 Conectando con Google Sheets...")
        worksheet = conectar_google_sheets()
        print(f"✅ Conectado a: {worksheet.title}")
        print()
        
        # 2. Leer respuestas
        print("📥 Leyendo respuestas del formulario...")
        df = leer_respuestas(worksheet)
        print(f"✅ Se encontraron {len(df)} respuestas")
        print()
        
        # 3. Transformar datos y guardar comentarios
        print("🔄 Transformando datos y guardando comentarios individuales...")
        datos = transformar_datos(df, db)
        print(f"✅ Datos transformados")
        print()
        
        # 4. Calcular promedios por curso
        print("📈 Calculando promedios por curso...")
        promedios = calcular_promedios_por_curso(datos)
        print(f"✅ Promedios calculados para {len(promedios)} cursos")
        print()
        
        # 5. Enviar a CONVIVIR v4.0
        print("📤 Enviando datos a CONVIVIR v4.0...")
        exitosos = 0
        for curso_data in promedios:
            if enviar_a_convivir(curso_data):
                exitosos += 1
        
        print()
        print(f"✅ {exitosos}/{len(promedios)} cursos importados exitosamente")
        
        # 6. Ejecutar análisis NLP
        resultado_nlp = ejecutar_analisis_nlp(db)
        
        print()
        print("=" * 70)
        print(f"✅ Proceso completado exitosamente")
        print("=" * 70)
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo de credenciales '{CREDENTIALS_FILE}'")
        print("   Por favor, descarga las credenciales de Google Cloud y colócalas en el mismo directorio.")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

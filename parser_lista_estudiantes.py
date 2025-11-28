"""
Parser para archivos de listas de estudiantes en formato .txt
Formato simplificado: N° | NOMBRE COMPLETO
Extrae automáticamente: número, nombre completo, género inferido
"""

import re
from datetime import datetime


def inferir_genero(nombre_completo):
    """
    Infiere el género basándose en nombres comunes chilenos
    """
    nombre_completo = nombre_completo.upper()
    
    # Nombres femeninos comunes
    nombres_femeninos = [
        'MARÍA', 'FERNANDA', 'VALENTINA', 'SOFÍA', 'CAMILA', 'JAVIERA', 'CONSTANZA',
        'FRANCISCA', 'CATALINA', 'MARTINA', 'ISIDORA', 'FLORENCIA', 'ANTONIA',
        'MONSERRAT', 'IGNACIA', 'AMANDA', 'CAROLINA', 'DANIELA', 'ANDREA', 'PAULA',
        'BEATRIZ', 'EMILIA', 'RENATA', 'TRINIDAD', 'ÁNGELA', 'BELÉN', 'PAZ',
        'XIOMARA', 'DAMARIT', 'LUISA', 'AYELÉEN', 'EMILY', 'PASCAL', 'SOL',
        'MONSERRATT', 'LILIANA'
    ]
    
    # Nombres masculinos comunes
    nombres_masculinos = [
        'JOSÉ', 'JUAN', 'CARLOS', 'LUIS', 'DIEGO', 'SEBASTIÁN', 'MATÍAS', 'NICOLÁS',
        'FELIPE', 'JOAQUÍN', 'BENJAMÍN', 'VICENTE', 'TOMÁS', 'CRISTÓBAL', 'IGNACIO',
        'JOSEMANUEL', 'CHRISTIANN', 'JHEYSON', 'RENATO', 'ALESSANDRO', 'LEONEL',
        'GIANLUCAS', 'AMARO', 'MARCELO', 'ALEXIS', 'JOHAO', 'PATRICIO', 'CIARAN',
        'DAVID', 'DEYMAR', 'AGUSTÍN', 'ALFONSO', 'ENRIQUE', 'RODRIGO', 'ANTONIO'
    ]
    
    # Buscar nombres femeninos
    for nombre in nombres_femeninos:
        if nombre in nombre_completo:
            return 'Femenino'
    
    # Buscar nombres masculinos
    for nombre in nombres_masculinos:
        if nombre in nombre_completo:
            return 'Masculino'
    
    # Por defecto, retornar basándose en terminaciones comunes
    if any(term in nombre_completo for term in ['A ', ' A', 'ANA', 'INA', 'ELA']):
        return 'Femenino'
    
    return 'Masculino'


def parsear_lista_estudiantes(contenido_archivo):
    """
    Parsea un archivo de lista de estudiantes en formato simplificado
    
    Formato esperado:
    N°  NOMBRE COMPLETO
    1   APELLIDO1 APELLIDO2 NOMBRE1 NOMBRE2
    2   APELLIDO1 APELLIDO2 NOMBRE1 NOMBRE2
    ...
    
    Args:
        contenido_archivo (str): Contenido del archivo .txt
    
    Returns:
        dict: {
            'exito': bool,
            'estudiantes': list,
            'total_estudiantes': int,
            'mensaje': str
        }
    """
    try:
        lineas = contenido_archivo.split('\n')
        estudiantes = []
        
        # Patrón para detectar líneas de estudiantes
        # Formato: N° seguido de NOMBRE COMPLETO (letras, espacios, acentos)
        patron = re.compile(
            r'^\s*(\d+)\s+([A-ZÁÉÍÓÚÑÜ\s]+)\s*$',
            re.IGNORECASE
        )
        
        for linea in lineas:
            # Saltar líneas vacías o de encabezado
            if not linea.strip() or 'NOMBRE COMPLETO' in linea.upper():
                continue
            
            match = patron.match(linea)
            if match:
                numero, nombre_completo = match.groups()
                
                # Limpiar nombre (eliminar espacios extras)
                nombre_completo = ' '.join(nombre_completo.split())
                
                # Inferir género
                genero = inferir_genero(nombre_completo)
                
                # Generar un RUN ficticio basado en el número (para compatibilidad)
                # Formato: 99.XXX.XXX-Y donde XXX es el número del estudiante
                run_base = 99000000 + int(numero)
                run = f"{run_base // 1000000}.{(run_base // 1000) % 1000:03d}.{run_base % 1000:03d}-{run_base % 10}"
                
                # Edad por defecto (14 años para enseñanza media)
                edad = 14
                
                estudiante = {
                    'numero': int(numero),
                    'run': run,
                    'nombre_completo': nombre_completo.title(),
                    'edad': edad,
                    'genero': genero
                }
                
                estudiantes.append(estudiante)
        
        if len(estudiantes) == 0:
            return {
                'exito': False,
                'mensaje': 'No se encontraron estudiantes en el archivo. Verifique el formato.',
                'estudiantes': [],
                'total_estudiantes': 0
            }
        
        return {
            'exito': True,
            'estudiantes': estudiantes,
            'total_estudiantes': len(estudiantes),
            'mensaje': f'{len(estudiantes)} estudiantes procesados exitosamente'
        }
        
    except Exception as e:
        return {
            'exito': False,
            'mensaje': f'Error al procesar archivo: {str(e)}',
            'estudiantes': [],
            'total_estudiantes': 0
        }


# Función de prueba
if __name__ == '__main__':
    # Ejemplo de uso
    with open('/home/ubuntu/upload/lista_1A.txt', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    resultado = parsear_lista_estudiantes(contenido)
    print(f"Éxito: {resultado['exito']}")
    print(f"Total estudiantes: {resultado['total_estudiantes']}")
    print(f"\nPrimeros 5 estudiantes:")
    for est in resultado['estudiantes'][:5]:
        print(f"  {est['numero']}. {est['nombre_completo']} ({est['genero']}, {est['edad']} años) - RUN: {est['run']}")


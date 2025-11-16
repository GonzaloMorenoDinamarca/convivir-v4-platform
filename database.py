"""
Módulo de Base de Datos SQLite para CONVIVIR v4.0
Gestiona la persistencia de datos con esquema normalizado
"""

import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import pandas as pd

Base = declarative_base()

# ============================================================================
# MODELOS DE DATOS (ORM)
# ============================================================================

class Cohorte(Base):
    """Representa un grupo de estudiantes que progresa junto a lo largo de los años"""
    __tablename__ = 'cohortes'
    
    cohorte_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cohorte = Column(String(200), nullable=False)  # ej. "Generación 2025-2028"
    ano_ingreso = Column(Integer, nullable=False)  # Año en que inició la cohorte
    fecha_creacion = Column(DateTime, default=datetime.now)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    cursos_anuales = relationship("CursoAnual", back_populates="cohorte")


class CursoAnual(Base):
    """Representa la asignación de un nombre de curso a una cohorte en un año específico"""
    __tablename__ = 'cursos_anuales'
    
    curso_anual_id = Column(Integer, primary_key=True, autoincrement=True)
    cohorte_id = Column(Integer, ForeignKey('cohortes.cohorte_id'), nullable=False)
    ano_academico = Column(Integer, nullable=False)
    nombre_curso = Column(String(50), nullable=False)  # ej. "1° A", "2° A"
    activo = Column(Boolean, default=True)  # Solo uno puede estar activo por cohorte
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    cohorte = relationship("Cohorte", back_populates="cursos_anuales")


class Establecimiento(Base):
    __tablename__ = 'establecimientos'
    
    id = Column(Integer, primary_key=True)
    establecimiento_id = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(200))
    region = Column(String(100))
    comuna = Column(String(100))
    tipo = Column(String(50))
    total_estudiantes = Column(Integer)
    total_docentes = Column(Integer)
    fecha_carga = Column(DateTime, default=datetime.now)
    
    # Relaciones
    cursos = relationship("CursoTemporal", back_populates="establecimiento")
    estudiantes = relationship("Estudiante", back_populates="establecimiento")


class CursoTemporal(Base):
    __tablename__ = 'cursos_temporal'
    
    id = Column(Integer, primary_key=True)
    establecimiento_id = Column(String(50), ForeignKey('establecimientos.establecimiento_id'))
    fecha_registro = Column(DateTime, nullable=False)
    periodo = Column(String(50))
    curso_id = Column(String(20), nullable=False)
    total_estudiantes = Column(Integer)
    clima_escolar_promedio = Column(Float)
    apoyo_docentes_promedio = Column(Float)
    participacion_estudiantes_promedio = Column(Float)
    nivel_empatia_promedio = Column(Float)
    nivel_autoestima_promedio = Column(Float)
    nivel_resolucion_conflictos_promedio = Column(Float)
    incidentes_bullying = Column(Integer)
    incidentes_violencia_fisica = Column(Integer)
    incidentes_discriminacion = Column(Integer)
    reportes_anonimos = Column(Integer)
    asistencia_promedio_porcentaje = Column(Float)
    promedio_notas = Column(Float)
    
    # Relaciones
    establecimiento = relationship("Establecimiento", back_populates="cursos")


class Estudiante(Base):
    __tablename__ = 'estudiantes'
    
    id = Column(Integer, primary_key=True)
    establecimiento_id = Column(String(50), ForeignKey('establecimientos.establecimiento_id'))
    estudiante_id = Column(String(50), unique=True, nullable=False)
    cohorte_id = Column(Integer, ForeignKey('cohortes.cohorte_id'))  # Vínculo permanente a la cohorte
    curso_id = Column(String(20))  # Mantener por compatibilidad con datos antiguos
    genero = Column(String(10))
    edad = Column(Integer)
    tiene_nee = Column(Boolean)
    prioritario = Column(Boolean)
    fecha_ingreso = Column(DateTime)
    nivel_socioeconomico = Column(String(50))
    
    # Relaciones
    establecimiento = relationship("Establecimiento", back_populates="estudiantes")
    evaluaciones = relationship("EvaluacionSocioemocional", back_populates="estudiante")
    comentarios = relationship("Comentario", back_populates="estudiante")


class EvaluacionSocioemocional(Base):
    __tablename__ = 'evaluaciones_socioemocionales'
    
    id = Column(Integer, primary_key=True)
    estudiante_id = Column(String(50), ForeignKey('estudiantes.estudiante_id'))
    fecha_evaluacion = Column(DateTime, nullable=False)
    periodo = Column(String(50))
    empatia_score = Column(Integer)
    autoestima_score = Column(Integer)
    resolucion_conflictos_score = Column(Integer)
    ansiedad_score = Column(Integer)
    bienestar_general_score = Column(Integer)
    instrumento_evaluacion = Column(String(100))
    
    # Relaciones
    estudiante = relationship("Estudiante", back_populates="evaluaciones")


class Comentario(Base):
    __tablename__ = 'comentarios'
    
    id = Column(Integer, primary_key=True)
    estudiante_id = Column(String(50), ForeignKey('estudiantes.estudiante_id'))
    fecha_comentario = Column(DateTime, nullable=False)
    periodo = Column(String(50))
    tipo_comentario = Column(String(50))
    comentario_texto = Column(Text)
    tema_principal = Column(String(100))
    tono_percibido = Column(String(20))
    sentimiento_analizado = Column(String(20))  # Resultado del NLP
    confianza_sentimiento = Column(Float)  # Confianza del modelo
    
    # Relaciones
    estudiante = relationship("Estudiante", back_populates="comentarios")


class Interaccion(Base):
    __tablename__ = 'interacciones_sociales'
    
    id = Column(Integer, primary_key=True)
    fecha_interaccion = Column(DateTime, nullable=False)
    estudiante_origen_id = Column(String(50), ForeignKey('estudiantes.estudiante_id'))
    estudiante_destino_id = Column(String(50), ForeignKey('estudiantes.estudiante_id'))
    tipo_interaccion = Column(String(50))
    intensidad = Column(Integer)
    contexto = Column(String(100))
    reportado_por = Column(String(50))
    
    # Relaciones eliminadas para evitar errores de SQLAlchemy
    # Las consultas se harán manualmente cuando sea necesario


class Intervencion(Base):
    __tablename__ = 'intervenciones'
    
    id = Column(Integer, primary_key=True)
    fecha_intervencion = Column(DateTime, nullable=False)
    periodo = Column(String(50))
    curso_id = Column(String(20))
    tipo_intervencion = Column(String(100))
    duracion_horas = Column(Float)
    participantes = Column(Integer)
    responsable = Column(String(100))
    objetivo = Column(String(50))
    evaluacion_efectividad = Column(Integer)


class Docente(Base):
    __tablename__ = 'docentes'
    
    id = Column(Integer, primary_key=True)
    docente_id = Column(String(50), unique=True, nullable=False)
    nombre_docente = Column(String(200))
    curso_jefatura = Column(String(20))
    asignaturas = Column(String(200))
    años_experiencia = Column(Integer)
    formacion_convivencia = Column(Boolean)
    carga_horaria_semanal = Column(Integer)


class Prediccion(Base):
    """Almacena predicciones generadas por modelos ML"""
    __tablename__ = 'predicciones'
    
    id = Column(Integer, primary_key=True)
    fecha_prediccion = Column(DateTime, default=datetime.now)
    curso_id = Column(String(20))
    tipo_prediccion = Column(String(50))  # 'riesgo', 'clima', 'incidentes'
    horizonte_semanas = Column(Integer)  # Cuántas semanas hacia adelante
    valor_predicho = Column(Float)
    intervalo_confianza_inferior = Column(Float)
    intervalo_confianza_superior = Column(Float)
    modelo_utilizado = Column(String(50))


class Alerta(Base):
    """Almacena alertas generadas por el sistema"""
    __tablename__ = 'alertas'
    
    id = Column(Integer, primary_key=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    tipo_alerta = Column(String(50))  # 'predictiva', 'social', 'sentimiento'
    nivel_prioridad = Column(String(20))  # 'baja', 'media', 'alta', 'crítica'
    curso_id = Column(String(20))
    estudiante_id = Column(String(50))
    mensaje = Column(Text)
    recomendacion = Column(Text)
    estado = Column(String(20), default='pendiente')  # 'pendiente', 'revisada', 'atendida'
    fecha_atencion = Column(DateTime)


# ============================================================================
# GESTOR DE BASE DE DATOS
# ============================================================================

class DatabaseManager:
    """Gestiona todas las operaciones con la base de datos"""
    
    def __init__(self, db_path='convivir.db'):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.SessionFactory = Session
    
    def get_session(self):
        """Context manager para obtener una sesión de base de datos"""
        from contextlib import contextmanager
        
        @contextmanager
        def session_scope():
            session = self.SessionFactory()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        
        return session_scope()
    
    def cargar_desde_excel(self, excel_path):
        """Carga datos desde el archivo Excel mejorado a la base de datos"""
        try:
            # Leer todas las hojas
            xl = pd.ExcelFile(excel_path)
            
            # 1. Metadata Establecimiento
            if 'Metadata_Establecimiento' in xl.sheet_names:
                df_meta = pd.read_excel(excel_path, sheet_name='Metadata_Establecimiento')
                for _, row in df_meta.iterrows():
                    # Verificar si ya existe
                    est_existente = self.session.query(Establecimiento).filter_by(
                        establecimiento_id=row['establecimiento_id']
                    ).first()
                    
                    if est_existente:
                        # Actualizar
                        est_existente.nombre = row['nombre_establecimiento']
                        est_existente.region = row['region']
                        est_existente.comuna = row['comuna']
                        est_existente.tipo = row['tipo_establecimiento']
                        est_existente.total_estudiantes = row['total_estudiantes_establecimiento']
                        est_existente.total_docentes = row['total_docentes']
                    else:
                        # Crear nuevo
                        est = Establecimiento(
                            establecimiento_id=row['establecimiento_id'],
                            nombre=row['nombre_establecimiento'],
                            region=row['region'],
                            comuna=row['comuna'],
                            tipo=row['tipo_establecimiento'],
                            total_estudiantes=row['total_estudiantes_establecimiento'],
                            total_docentes=row['total_docentes']
                        )
                        self.session.add(est)
            
            # 2. Cursos Temporal
            if 'Cursos_Temporal' in xl.sheet_names:
                df_cursos = pd.read_excel(excel_path, sheet_name='Cursos_Temporal')
                for _, row in df_cursos.iterrows():
                    curso = CursoTemporal(
                        establecimiento_id=df_meta.iloc[0]['establecimiento_id'] if 'Metadata_Establecimiento' in xl.sheet_names else 'EST_001',
                        fecha_registro=pd.to_datetime(row['fecha_registro']),
                        periodo=row['periodo'],
                        curso_id=row['curso_id'],
                        total_estudiantes=row['total_estudiantes'],
                        clima_escolar_promedio=row['clima_escolar_promedio'],
                        apoyo_docentes_promedio=row['apoyo_docentes_promedio'],
                        participacion_estudiantes_promedio=row['participacion_estudiantes_promedio'],
                        nivel_empatia_promedio=row['nivel_empatia_promedio'],
                        nivel_autoestima_promedio=row['nivel_autoestima_promedio'],
                        nivel_resolucion_conflictos_promedio=row['nivel_resolucion_conflictos_promedio'],
                        incidentes_bullying=row['incidentes_bullying'],
                        incidentes_violencia_fisica=row['incidentes_violencia_fisica'],
                        incidentes_discriminacion=row['incidentes_discriminacion'],
                        reportes_anonimos=row['reportes_anonimos'],
                        asistencia_promedio_porcentaje=row.get('asistencia_promedio_porcentaje', None),
                        promedio_notas=row.get('promedio_notas', None)
                    )
                    self.session.add(curso)
            
            # 3. Estudiantes
            if 'Estudiantes' in xl.sheet_names:
                df_est = pd.read_excel(excel_path, sheet_name='Estudiantes')
                for _, row in df_est.iterrows():
                    # Verificar si ya existe
                    est_existente = self.session.query(Estudiante).filter_by(
                        estudiante_id=row['estudiante_id']
                    ).first()
                    
                    if est_existente:
                        # Actualizar
                        est_existente.curso_id = row['curso_id']
                        est_existente.genero = row.get('genero', None)
                        est_existente.edad = row.get('edad', None)
                        est_existente.tiene_nee = row.get('tiene_nee', False)
                        est_existente.prioritario = row.get('prioritario', False)
                        est_existente.nivel_socioeconomico = row.get('nivel_socioeconomico', None)
                    else:
                        # Crear nuevo
                        estudiante = Estudiante(
                            establecimiento_id=df_meta.iloc[0]['establecimiento_id'] if 'Metadata_Establecimiento' in xl.sheet_names else 'EST_001',
                            estudiante_id=row['estudiante_id'],
                            curso_id=row['curso_id'],
                            genero=row.get('genero', None),
                            edad=row.get('edad', None),
                            tiene_nee=row.get('tiene_nee', False),
                            prioritario=row.get('prioritario', False),
                            fecha_ingreso=pd.to_datetime(row['fecha_ingreso_establecimiento']) if 'fecha_ingreso_establecimiento' in row else None,
                            nivel_socioeconomico=row.get('nivel_socioeconomico', None)
                        )
                        self.session.add(estudiante)
            
            # 4. Evaluaciones Socioemocionales
            if 'Evaluaciones_Socioemocionales' in xl.sheet_names:
                df_eval = pd.read_excel(excel_path, sheet_name='Evaluaciones_Socioemocionales')
                for _, row in df_eval.iterrows():
                    evaluacion = EvaluacionSocioemocional(
                        estudiante_id=row['estudiante_id'],
                        fecha_evaluacion=pd.to_datetime(row['fecha_evaluacion']),
                        periodo=row['periodo'],
                        empatia_score=row['empatia_score'],
                        autoestima_score=row['autoestima_score'],
                        resolucion_conflictos_score=row['resolucion_conflictos_score'],
                        ansiedad_score=row.get('ansiedad_score', None),
                        bienestar_general_score=row.get('bienestar_general_score', None),
                        instrumento_evaluacion=row.get('instrumento_evaluacion', 'No especificado')
                    )
                    self.session.add(evaluacion)
            
            # 5. Comentarios
            if 'Comentarios_Estudiantes' in xl.sheet_names:
                df_com = pd.read_excel(excel_path, sheet_name='Comentarios_Estudiantes')
                for _, row in df_com.iterrows():
                    comentario = Comentario(
                        estudiante_id=row['estudiante_id'],
                        fecha_comentario=pd.to_datetime(row['fecha_comentario']),
                        periodo=row['periodo'],
                        tipo_comentario=row.get('tipo_comentario', 'No especificado'),
                        comentario_texto=row['comentario_texto'],
                        tema_principal=row.get('tema_principal', None),
                        tono_percibido=row.get('tono_percibido', None)
                    )
                    self.session.add(comentario)
            
            # 6. Interacciones Sociales
            if 'Interacciones_Sociales' in xl.sheet_names:
                df_int = pd.read_excel(excel_path, sheet_name='Interacciones_Sociales')
                for _, row in df_int.iterrows():
                    interaccion = Interaccion(
                        fecha_interaccion=pd.to_datetime(row['fecha_interaccion']),
                        estudiante_origen_id=row['estudiante_origen_id'],
                        estudiante_destino_id=row['estudiante_destino_id'],
                        tipo_interaccion=row['tipo_interaccion'],
                        intensidad=row['intensidad'],
                        contexto=row.get('contexto', None),
                        reportado_por=row.get('reportado_por', None)
                    )
                    self.session.add(interaccion)
            
            # 7. Intervenciones
            if 'Intervenciones_Aplicadas' in xl.sheet_names:
                df_interv = pd.read_excel(excel_path, sheet_name='Intervenciones_Aplicadas')
                for _, row in df_interv.iterrows():
                    intervencion = Intervencion(
                        fecha_intervencion=pd.to_datetime(row['fecha_intervencion']),
                        periodo=row['periodo'],
                        curso_id=row.get('curso_id', None),
                        tipo_intervencion=row['tipo_intervencion'],
                        duracion_horas=row.get('duracion_horas', None),
                        participantes=row.get('participantes', None),
                        responsable=row.get('responsable', None),
                        objetivo=row.get('objetivo', None),
                        evaluacion_efectividad=row.get('evaluacion_efectividad', None)
                    )
                    self.session.add(intervencion)
            
            # 8. Docentes
            if 'Docentes' in xl.sheet_names:
                df_doc = pd.read_excel(excel_path, sheet_name='Docentes')
                for _, row in df_doc.iterrows():
                    # Verificar si ya existe
                    doc_existente = self.session.query(Docente).filter_by(
                        docente_id=row['docente_id']
                    ).first()
                    
                    if doc_existente:
                        # Actualizar
                        doc_existente.nombre_docente = row.get('nombre_docente', None)
                        doc_existente.curso_jefatura = row.get('curso_jefatura', None)
                        doc_existente.asignaturas = row.get('asignaturas', None)
                        doc_existente.años_experiencia = row.get('años_experiencia', None)
                        doc_existente.formacion_convivencia = row.get('formacion_convivencia', False)
                        doc_existente.carga_horaria_semanal = row.get('carga_horaria_semanal', None)
                    else:
                        # Crear nuevo
                        docente = Docente(
                            docente_id=row['docente_id'],
                            nombre_docente=row.get('nombre_docente', None),
                            curso_jefatura=row.get('curso_jefatura', None),
                            asignaturas=row.get('asignaturas', None),
                            años_experiencia=row.get('años_experiencia', None),
                            formacion_convivencia=row.get('formacion_convivencia', False),
                            carga_horaria_semanal=row.get('carga_horaria_semanal', None)
                        )
                        self.session.add(docente)
            
            self.session.commit()
            return {'exito': True, 'mensaje': 'Datos cargados exitosamente a la base de datos'}
        
        except Exception as e:
            self.session.rollback()
            return {'exito': False, 'mensaje': f'Error al cargar datos: {str(e)}'}
    
    def obtener_series_temporales_curso(self, curso_id):
        """Obtiene la serie temporal de un curso para análisis LSTM"""
        cursos = self.session.query(CursoTemporal).filter_by(curso_id=curso_id).order_by(CursoTemporal.fecha_registro).all()
        
        data = []
        for c in cursos:
            data.append({
                'fecha': c.fecha_registro,
                'clima_escolar': c.clima_escolar_promedio,
                'apoyo_docentes': c.apoyo_docentes_promedio,
                'participacion': c.participacion_estudiantes_promedio,
                'empatia': c.nivel_empatia_promedio,
                'autoestima': c.nivel_autoestima_promedio,
                'resolucion_conflictos': c.nivel_resolucion_conflictos_promedio,
                'incidentes_bullying': c.incidentes_bullying,
                'incidentes_violencia': c.incidentes_violencia_fisica,
                'incidentes_discriminacion': c.incidentes_discriminacion
            })
        
        return pd.DataFrame(data)
    
    def obtener_grafo_social(self):
        """Obtiene todas las interacciones para construir el grafo social"""
        interacciones = self.session.query(Interaccion).all()
        
        edges = []
        for i in interacciones:
            edges.append({
                'origen': i.estudiante_origen_id,
                'destino': i.estudiante_destino_id,
                'tipo': i.tipo_interaccion,
                'intensidad': i.intensidad,
                'fecha': i.fecha_interaccion
            })
        
        return pd.DataFrame(edges)
    
    def obtener_comentarios_para_nlp(self):
        """Obtiene todos los comentarios para análisis NLP"""
        comentarios = self.session.query(Comentario).all()
        
        data = []
        for c in comentarios:
            data.append({
                'id': c.id,
                'estudiante_id': c.estudiante_id,
                'fecha': c.fecha_comentario,
                'texto': c.comentario_texto,
                'tema': c.tema_principal,
                'tono_percibido': c.tono_percibido
            })
        
        return pd.DataFrame(data)
    
    def guardar_prediccion(self, curso_id, tipo_prediccion, horizonte_semanas, valor_predicho, 
                          intervalo_inf, intervalo_sup, modelo):
        """Guarda una predicción en la base de datos"""
        pred = Prediccion(
            curso_id=curso_id,
            tipo_prediccion=tipo_prediccion,
            horizonte_semanas=horizonte_semanas,
            valor_predicho=valor_predicho,
            intervalo_confianza_inferior=intervalo_inf,
            intervalo_confianza_superior=intervalo_sup,
            modelo_utilizado=modelo
        )
        self.session.add(pred)
        self.session.commit()
    
    def crear_alerta(self, tipo_alerta, nivel_prioridad, mensaje, recomendacion, 
                    curso_id=None, estudiante_id=None):
        """Crea una nueva alerta en el sistema"""
        alerta = Alerta(
            tipo_alerta=tipo_alerta,
            nivel_prioridad=nivel_prioridad,
            curso_id=curso_id,
            estudiante_id=estudiante_id,
            mensaje=mensaje,
            recomendacion=recomendacion
        )
        self.session.add(alerta)
        self.session.commit()
        return alerta.id
    
    def obtener_alertas_pendientes(self):
        """Obtiene todas las alertas pendientes"""
        alertas = self.session.query(Alerta).filter_by(estado='pendiente').order_by(Alerta.fecha_creacion.desc()).all()
        
        data = []
        for a in alertas:
            data.append({
                'id': a.id,
                'fecha': a.fecha_creacion,
                'tipo': a.tipo_alerta,
                'prioridad': a.nivel_prioridad,
                'curso': a.curso_id,
                'estudiante': a.estudiante_id,
                'mensaje': a.mensaje,
                'recomendacion': a.recomendacion
            })
        
        return pd.DataFrame(data)
    
    def close(self):
        """Cierra la sesión de base de datos"""
        self.session.close()


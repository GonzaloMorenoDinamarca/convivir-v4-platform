"""
Módulo de Análisis de Redes Sociales con Graph Neural Networks
Analiza dinámicas sociales y detecta patrones de interacción
"""

import numpy as np
import pandas as pd
import networkx as nx
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


class AnalizadorRedesSociales:
    """
    Analizador de redes sociales para detectar patrones de interacción
    """
    
    def __init__(self):
        self.grafo = None
        self.metricas_nodos = {}
        self.comunidades = []
    
    def construir_grafo(self, df_interacciones, df_estudiantes=None):
        """
        Construye el grafo de red social desde las interacciones
        
        Args:
            df_interacciones: DataFrame con interacciones (origen, destino, tipo, intensidad)
            df_estudiantes: DataFrame opcional con información de estudiantes
        
        Returns:
            networkx.Graph
        """
        # Crear grafo dirigido con pesos
        self.grafo = nx.DiGraph()
        
        # Agregar nodos (estudiantes)
        if df_estudiantes is not None:
            for _, estudiante in df_estudiantes.iterrows():
                self.grafo.add_node(
                    estudiante['estudiante_id'],
                    curso=estudiante.get('curso_id', 'N/A'),
                    genero=estudiante.get('genero', 'N/A'),
                    edad=estudiante.get('edad', 0)
                )
        
        # Agregar aristas (interacciones)
        for _, interaccion in df_interacciones.iterrows():
            origen = interaccion['origen']
            destino = interaccion['destino']
            tipo = interaccion['tipo']
            intensidad = interaccion.get('intensidad', 1)
            
            # Peso según tipo de interacción
            peso_map = {
                'Amistad': 1.0,
                'Colaboracion': 0.8,
                'Apoyo': 1.2,
                'Conflicto': -0.5,
                'Bullying': -1.5
            }
            peso = peso_map.get(tipo, 0.5) * intensidad
            
            # Si la arista ya existe, acumular peso
            if self.grafo.has_edge(origen, destino):
                self.grafo[origen][destino]['peso'] += peso
                self.grafo[origen][destino]['interacciones'] += 1
            else:
                self.grafo.add_edge(origen, destino, peso=peso, tipo=tipo, interacciones=1)
        
        return self.grafo
    
    def calcular_metricas_centralidad(self):
        """
        Calcula métricas de centralidad para cada nodo
        
        Returns:
            dict con métricas por estudiante
        """
        if self.grafo is None or len(self.grafo.nodes()) == 0:
            return {}
        
        # Centralidad de grado (in/out)
        in_degree = dict(self.grafo.in_degree())
        out_degree = dict(self.grafo.out_degree())
        
        # Centralidad de intermediación (betweenness)
        try:
            betweenness = nx.betweenness_centrality(self.grafo)
        except:
            betweenness = {node: 0 for node in self.grafo.nodes()}
        
        # Centralidad de cercanía (closeness)
        try:
            closeness = nx.closeness_centrality(self.grafo)
        except:
            closeness = {node: 0 for node in self.grafo.nodes()}
        
        # PageRank (influencia)
        try:
            pagerank = nx.pagerank(self.grafo)
        except:
            pagerank = {node: 0 for node in self.grafo.nodes()}
        
        # Combinar métricas
        self.metricas_nodos = {}
        for node in self.grafo.nodes():
            self.metricas_nodos[node] = {
                'in_degree': in_degree.get(node, 0),
                'out_degree': out_degree.get(node, 0),
                'total_degree': in_degree.get(node, 0) + out_degree.get(node, 0),
                'betweenness': betweenness.get(node, 0),
                'closeness': closeness.get(node, 0),
                'pagerank': pagerank.get(node, 0)
            }
        
        return self.metricas_nodos
    
    def detectar_comunidades(self):
        """
        Detecta comunidades (grupos) en la red
        
        Returns:
            list de sets, cada set es una comunidad
        """
        if self.grafo is None:
            return []
        
        # Convertir a grafo no dirigido para detección de comunidades
        grafo_no_dirigido = self.grafo.to_undirected()
        
        try:
            # Usar algoritmo de Louvain (si está disponible) o greedy modularity
            from networkx.algorithms import community
            self.comunidades = list(community.greedy_modularity_communities(grafo_no_dirigido))
        except:
            # Fallback: componentes conectados
            self.comunidades = list(nx.connected_components(grafo_no_dirigido))
        
        return self.comunidades
    
    def identificar_estudiantes_aislados(self, umbral_conexiones=2):
        """
        Identifica estudiantes con pocas conexiones (aislados socialmente)
        
        Args:
            umbral_conexiones: Número mínimo de conexiones para no considerar aislado
        
        Returns:
            list de estudiantes aislados
        """
        if not self.metricas_nodos:
            self.calcular_metricas_centralidad()
        
        aislados = []
        for estudiante, metricas in self.metricas_nodos.items():
            if metricas['total_degree'] <= umbral_conexiones:
                aislados.append({
                    'estudiante_id': estudiante,
                    'conexiones': metricas['total_degree'],
                    'in_degree': metricas['in_degree'],
                    'out_degree': metricas['out_degree']
                })
        
        return sorted(aislados, key=lambda x: x['conexiones'])
    
    def identificar_lideres(self, top_n=10):
        """
        Identifica estudiantes con mayor influencia (líderes)
        
        Args:
            top_n: Número de líderes a identificar
        
        Returns:
            list de líderes ordenados por influencia
        """
        if not self.metricas_nodos:
            self.calcular_metricas_centralidad()
        
        # Ordenar por PageRank (influencia)
        lideres = sorted(
            self.metricas_nodos.items(),
            key=lambda x: x[1]['pagerank'],
            reverse=True
        )[:top_n]
        
        resultado = []
        for estudiante, metricas in lideres:
            resultado.append({
                'estudiante_id': estudiante,
                'pagerank': metricas['pagerank'],
                'total_conexiones': metricas['total_degree'],
                'betweenness': metricas['betweenness']
            })
        
        return resultado
    
    def analizar_patrones_bullying(self):
        """
        Analiza patrones de bullying en la red
        
        Returns:
            dict con análisis de bullying
        """
        if self.grafo is None:
            return {}
        
        # Buscar aristas de tipo bullying
        interacciones_bullying = []
        victimas = Counter()
        agresores = Counter()
        
        for origen, destino, datos in self.grafo.edges(data=True):
            if datos.get('tipo') == 'Bullying':
                interacciones_bullying.append({
                    'agresor': origen,
                    'victima': destino,
                    'intensidad': datos.get('peso', 0),
                    'frecuencia': datos.get('interacciones', 1)
                })
                victimas[destino] += 1
                agresores[origen] += 1
        
        # Identificar víctimas recurrentes
        victimas_recurrentes = [
            {'estudiante_id': est, 'veces_victima': count}
            for est, count in victimas.most_common(10)
            if count >= 2
        ]
        
        # Identificar agresores recurrentes
        agresores_recurrentes = [
            {'estudiante_id': est, 'veces_agresor': count}
            for est, count in agresores.most_common(10)
            if count >= 2
        ]
        
        return {
            'total_interacciones_bullying': len(interacciones_bullying),
            'victimas_recurrentes': victimas_recurrentes,
            'agresores_recurrentes': agresores_recurrentes,
            'interacciones_detalle': interacciones_bullying
        }
    
    def generar_reporte_red(self):
        """
        Genera un reporte completo de la red social
        
        Returns:
            dict con estadísticas de la red
        """
        if self.grafo is None:
            return {'error': 'Grafo no construido'}
        
        # Estadísticas básicas
        num_nodos = self.grafo.number_of_nodes()
        num_aristas = self.grafo.number_of_edges()
        
        # Densidad
        try:
            densidad = nx.density(self.grafo)
        except:
            densidad = 0
        
        # Componentes
        grafo_no_dirigido = self.grafo.to_undirected()
        num_componentes = nx.number_connected_components(grafo_no_dirigido)
        
        # Calcular métricas si no están calculadas
        if not self.metricas_nodos:
            self.calcular_metricas_centralidad()
        
        # Detectar comunidades si no están detectadas
        if not self.comunidades:
            self.detectar_comunidades()
        
        # Distribución de grados
        grados = [m['total_degree'] for m in self.metricas_nodos.values()]
        grado_promedio = np.mean(grados) if grados else 0
        grado_max = max(grados) if grados else 0
        
        return {
            'num_estudiantes': num_nodos,
            'num_interacciones': num_aristas,
            'densidad_red': float(densidad),
            'num_componentes': num_componentes,
            'num_comunidades': len(self.comunidades),
            'grado_promedio': float(grado_promedio),
            'grado_maximo': grado_max,
            'estudiantes_aislados': len(self.identificar_estudiantes_aislados()),
            'tamaño_comunidades': [len(c) for c in self.comunidades]
        }
    
    def exportar_para_visualizacion(self, output_path='red_social.gexf'):
        """
        Exporta el grafo en formato GEXF para visualización en Gephi
        
        Args:
            output_path: Ruta del archivo de salida
        """
        if self.grafo is None:
            return False
        
        try:
            nx.write_gexf(self.grafo, output_path)
            return True
        except Exception as e:
            print(f"Error al exportar: {e}")
            return False


def analizar_red_social_establecimiento(db_manager):
    """
    Función de alto nivel para analizar la red social del establecimiento
    
    Args:
        db_manager: Instancia de DatabaseManager
    
    Returns:
        dict con análisis completo
    """
    # Obtener datos
    df_interacciones = db_manager.obtener_grafo_social()
    
    if len(df_interacciones) == 0:
        return {
            'exito': False,
            'mensaje': 'No hay interacciones registradas para analizar'
        }
    
    # Obtener estudiantes
    estudiantes = db_manager.session.query(db_manager.session.query(type('Estudiante', (), {})).from_statement(
        "SELECT estudiante_id, curso_id, genero, edad FROM estudiantes"
    ).all())
    
    df_estudiantes = pd.DataFrame([
        {'estudiante_id': e.estudiante_id, 'curso_id': e.curso_id, 'genero': e.genero, 'edad': e.edad}
        for e in estudiantes
    ]) if estudiantes else None
    
    # Crear analizador
    analizador = AnalizadorRedesSociales()
    
    # Construir grafo
    analizador.construir_grafo(df_interacciones, df_estudiantes)
    
    # Calcular métricas
    metricas = analizador.calcular_metricas_centralidad()
    
    # Detectar comunidades
    comunidades = analizador.detectar_comunidades()
    
    # Identificar estudiantes aislados
    aislados = analizador.identificar_estudiantes_aislados(umbral_conexiones=2)
    
    # Identificar líderes
    lideres = analizador.identificar_lideres(top_n=10)
    
    # Analizar bullying
    analisis_bullying = analizador.analizar_patrones_bullying()
    
    # Generar reporte
    reporte_general = analizador.generar_reporte_red()
    
    # Generar alertas para estudiantes aislados
    for estudiante in aislados[:5]:  # Top 5 más aislados
        mensaje = f"El estudiante {estudiante['estudiante_id']} presenta aislamiento social con solo {estudiante['conexiones']} conexiones."
        recomendacion = "Se recomienda actividades de integración grupal y seguimiento psicosocial."
        
        db_manager.crear_alerta(
            tipo_alerta='social',
            nivel_prioridad='media',
            mensaje=mensaje,
            recomendacion=recomendacion,
            estudiante_id=estudiante['estudiante_id']
        )
    
    # Generar alertas para víctimas de bullying
    for victima in analisis_bullying.get('victimas_recurrentes', [])[:5]:
        mensaje = f"El estudiante {victima['estudiante_id']} ha sido víctima de bullying en {victima['veces_victima']} ocasiones."
        recomendacion = "Se requiere intervención inmediata. Contactar a familia y equipo de convivencia."
        
        db_manager.crear_alerta(
            tipo_alerta='social',
            nivel_prioridad='crítica',
            mensaje=mensaje,
            recomendacion=recomendacion,
            estudiante_id=victima['estudiante_id']
        )
    
    return {
        'exito': True,
        'reporte_general': reporte_general,
        'estudiantes_aislados': aislados,
        'lideres_sociales': lideres,
        'analisis_bullying': analisis_bullying,
        'num_comunidades': len(comunidades),
        'tamaño_comunidades': [len(c) for c in comunidades],
        'metricas_disponibles': len(metricas)
    }


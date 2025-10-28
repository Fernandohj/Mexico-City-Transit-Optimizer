#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buscador_rutas.py

Lógica principal para encontrar la ruta más rápida en la red de
transporte público de la CDMX (Metro, Metrobús, Trolebús).

Utiliza el algoritmo de Dijkstra para buscar la ruta más rápida en tiempo,
calculando costos y manejando restricciones de cierres.
"""

# ---------------------------
# IMPORTACIONES
# ---------------------------
import heapq
from collections import defaultdict

# Importamos los datos de la red (líneas, tiempos, tarifas)
from datos_red_transporte import (
    metro_lines, metrobus_lines, trolebus_lines,
    TIME_METRO, TIME_METROBUS, TIME_TROLEBUS,
    TRANSFER_PENALTY, FARE_METRO, FARE_METROBUS,
    FARE_TROLEBUS, MAX_DISPLAY
)

# ---------------------------
# UTILIDADES
# ---------------------------
def normalizar(texto: str) -> str:
    """
    Convierte un nombre de estación a un formato estándar (minúsculas, sin
    acentos, guiones o paréntesis) para facilitar comparaciones.
    """
    if texto is None:
        return ""
    t = texto.strip().lower()
    # Reemplaza caracteres variables por espacios
    for ch in ['(', ')', '/', '-', '—', '–']:
        t = t.replace(ch, ' ')
    # Colapsa múltiples espacios en uno solo
    t = ' '.join(t.split())
    return t

# ---------------------------
# CONSTRUCCIÓN DEL GRAFO
# ---------------------------
def construir_grafo(estaciones_cerradas=None, tramos_cerrados=None):
    """
    Construye la red (grafo) a partir de las listas de líneas.
    
    - Cada nodo es: (estacion_original, sistema, id_linea)
    - Cada arista es: (vecino, tiempo_minutos, etiqueta_modo)
    
    Devuelve (grafo, indice_por_nombre)
    """

    # Usar 'sets' para búsquedas rápidas de estaciones/tramos cerrados
    estaciones_cerradas = set(normalizar(s) for s in (estaciones_cerradas or []) if s and s.strip() != '')
    closed_segments_norm = set()

    for seg in (tramos_cerrados or []):
        # Acepta formatos como (A, B, SIS), (A, B), o "A-B"
        if isinstance(seg, tuple) and len(seg) == 3:
            a,b,sys = seg
            closed_segments_norm.add((normalizar(a), normalizar(b), sys))
            closed_segments_norm.add((normalizar(b), normalizar(a), sys))
        elif isinstance(seg, tuple) and len(seg) == 2:
            a,b = seg
            closed_segments_norm.add((normalizar(a), normalizar(b), 'ANY'))
            closed_segments_norm.add((normalizar(b), normalizar(a), 'ANY'))
        elif isinstance(seg, str) and "-" in seg:
            a,b = seg.split("-", 1)
            closed_segments_norm.add((normalizar(a), normalizar(b), 'ANY'))
            closed_segments_norm.add((normalizar(b), normalizar(a), 'ANY'))

    grafo = defaultdict(list)
    nodos = set() # Almacena todos los nodos únicos creados

    # --- Funciones internas para construir el grafo ---
    
    def anadir_arista(nodo_a, nodo_b, tiempo, etiqueta):
        # Añade una conexión (arista) al grafo
        grafo[nodo_a].append((nodo_b, tiempo, etiqueta))

    def agregar_sistema(lineas_dict, nombre_sistema, tiempo_por_tramo):
        # Procesa un sistema completo (ej. 'METRO') y lo añade al grafo
        for id_linea, estaciones in lineas_dict.items():
            for est in estaciones:
                if normalizar(est) not in estaciones_cerradas:
                    nodos.add((est, nombre_sistema, id_linea))
            
            # Conectar estaciones contiguas (si no están cerradas)
            for i in range(len(estaciones)-1):
                a = estaciones[i]
                b = estaciones[i+1]
                na = normalizar(a); nb = normalizar(b)

                if na in estaciones_cerradas or nb in estaciones_cerradas:
                    continue
                if (na, nb, nombre_sistema) in closed_segments_norm or (na, nb, 'ANY') in closed_segments_norm:
                    continue
                
                nodo_a = (a, nombre_sistema, id_linea)
                nodo_b = (b, nombre_sistema, id_linea)
                anadir_arista(nodo_a, nodo_b, tiempo_por_tramo, nombre_sistema)
                anadir_arista(nodo_b, nodo_a, tiempo_por_tramo, nombre_sistema)
    
    # --- Ejecución de la construcción ---

    agregar_sistema(metro_lines, 'METRO', TIME_METRO)
    agregar_sistema(metrobus_lines, 'METROBUS', TIME_METROBUS)
    agregar_sistema(trolebus_lines, 'TROLEBUS', TIME_TROLEBUS)

    # CREAR TRANSBORDOS AUTOMÁTICOS
    # Conecta nodos que comparten el mismo nombre normalizado
    indice_por_nombre = defaultdict(list)
    for nodo in list(nodos):
        indice_por_nombre[normalizar(nodo[0])].append(nodo)

    for lista_nodos in indice_por_nombre.values():
        if len(lista_nodos) > 1:
            for i in range(len(lista_nodos)):
                for j in range(i+1, len(lista_nodos)):
                    a = lista_nodos[i]; b = lista_nodos[j]
                    anadir_arista(a, b, TRANSFER_PENALTY, 'TRANSFER')
                    anadir_arista(b, a, TRANSFER_PENALTY, 'TRANSFER')
    
    # Devolvemos el grafo y el índice (optimización)
    return grafo, indice_por_nombre

# ---------------------------
# ALGORITMO DE BÚSQUEDA
# ---------------------------
def encontrar_ruta_mas_rapida(grafo, indice_por_nombre, origen_nombre, destino_nombre):
    """
    Busca la ruta más rápida usando Dijkstra.
    El 'estado' del algoritmo incluye (nodo_actual, ultimo_sistema)
    para poder calcular correctamente las tarifas al cambiar de sistema.
    """

    origen_norm = normalizar(origen_nombre)
    destino_norm = normalizar(destino_nombre)

    # Optimización: Usar el índice para encontrar nodos de inicio/fin
    nodos_origen = indice_por_nombre.get(origen_norm, [])
    nodos_destino = set(indice_por_nombre.get(destino_norm, []))

    if not nodos_origen:
        raise ValueError(f"Origen no encontrado: '{origen_nombre}'")
    if not nodos_destino:
        raise ValueError(f"Destino no encontrado: '{destino_nombre}'")

    # Estructuras de Dijkstra
    heap = [] # (tiempo_acumulado, (nodo_actual, last_system))
    dist = {} # (nodo, last_system) -> mejor_tiempo
    prev = {} # (nodo, last_system) -> estado_anterior

    # Inicializar la cola con todos los posibles nodos de origen
    for nodo_inicio in nodos_origen:
        sistema_inicial = nodo_inicio[1] # METRO, METROBUS, etc.
        estado_inicial = (nodo_inicio, sistema_inicial)
        dist[estado_inicial] = 0.0
        prev[estado_inicial] = None
        heapq.heappush(heap, (0.0, estado_inicial))

    mejor_estado_final = None
    mejor_tiempo = float('inf')

    # Bucle principal de Dijkstra
    while heap:
        tiempo_actual, (nodo_actual, last_system) = heapq.heappop(heap)

        if tiempo_actual > dist.get((nodo_actual, last_system), float('inf')):
            continue # Ruta ya visitada con un tiempo menor

        # Si llegamos a un nodo destino, es la ruta más corta
        if nodo_actual in nodos_destino:
            mejor_estado_final = (nodo_actual, last_system)
            mejor_tiempo = tiempo_actual
            break

        # Explorar vecinos
        for vecino, tiempo_tramo, etiqueta in grafo[nodo_actual]:
            
            # Determinar cuál es el "último sistema" después de movernos
            nuevo_last = vecino[1] if etiqueta == 'TRANSFER' else etiqueta
            
            nuevo_estado = (vecino, nuevo_last)
            nuevo_tiempo = tiempo_actual + tiempo_tramo

            if nuevo_tiempo < dist.get(nuevo_estado, float('inf')):
                dist[nuevo_estado] = nuevo_tiempo
                prev[nuevo_estado] = (nodo_actual, last_system)
                heapq.heappush(heap, (nuevo_tiempo, nuevo_estado))

    if mejor_estado_final is None:
        return None # No se encontró ruta

    # --- Reconstruir la ruta y calcular costos ---

    # 1. Reconstruir ruta (viene en orden: destino -> origen)
    path_states = []
    cur = mejor_estado_final
    while cur is not None:
        path_states.append(cur[0]) # Solo nos importa el nodo (est, sis, lin)
        cur = prev.get(cur)
    
    ruta_simple = list(reversed(path_states)) # Invertir a: origen -> destino

    # 2. Calcular costo (cobrar solo al cambiar de sistema)
    costo_total = 0
    sistema_previo = None
    tarifas = {'METRO': FARE_METRO, 'METROBUS': FARE_METROBUS, 'TROLEBUS': FARE_TROLEBUS}
    
    for nodo in ruta_simple:
        sistema_actual = nodo[1]
        if sistema_actual != sistema_previo:
            costo_total += tarifas.get(sistema_actual, 0)
            sistema_previo = sistema_actual

    # 3. Agrupar en segmentos (tramos continuos en la misma línea)
    segmentos = []
    if ruta_simple:
        cur_sys, cur_line = ruta_simple[0][1], ruta_simple[0][2]
        estaciones_segmento = [ruta_simple[0][0]]
        
        for estacion, sys, linea in ruta_simple[1:]:
            if sys == cur_sys and linea == cur_line:
                estaciones_segmento.append(estacion)
            else:
                segmentos.append({"sistema": cur_sys, "linea": cur_line, "estaciones": estaciones_segmento})
                cur_sys, cur_line = sys, linea
                estaciones_segmento = [estacion]
        
        segmentos.append({"sistema": cur_sys, "linea": cur_line, "estaciones": estaciones_segmento})

    return {
        "tiempo_min": round(mejor_tiempo, 2),
        "segmentos": segmentos,
        "camino_completo": ruta_simple,
        "costo_mxn": costo_total
    }

# ---------------------------
# FUNCIONES DE INTERFAZ (Input/Output)
# ---------------------------
def imprimir_ruta(route_info, origen, destino):
    """Formatea y muestra la ruta encontrada en la consola."""
    
    if route_info is None:
        print("\nNo se encontró ninguna ruta disponible con las restricciones dadas.")
        return

    print(f"\n--- Ruta más rápida: {origen}  →  {destino} ---")
    print(f"Tiempo estimado: {route_info['tiempo_min']} minutos")
    print(f"Costo estimado: ${route_info['costo_mxn']:.2f} MXN")
    print("\nSegmentos del viaje:")

    for i, seg in enumerate(route_info['segmentos'], start=1):
        print(f"  {i}) {seg['sistema']} (Línea {seg['linea']}): {seg['estaciones'][0]}  →  {seg['estaciones'][-1]}")
        
        # Mostrar transbordo si no es el último segmento
        if i < len(route_info['segmentos']):
            estacion_transbordo = route_info['segmentos'][i]['estaciones'][0]
            print(f"     └─ Transbordo en: {estacion_transbordo}")

    # Opcional: Mostrar camino completo si no es gigante
    if len(route_info['camino_completo']) <= MAX_DISPLAY:
        print("\nCamino completo (Estación (Sistema-Línea)):")
        camino_str = "  →  ".join([f"{est} ({sys}-{ln})" for (est, sys, ln) in route_info['camino_completo']])
        print("  " + camino_str)

def parsear_tramos_cerrados(raw: str):
    """
    Convierte un string de tramos (ej: "A-B, C-D:METRO")
    en una lista de tuplas (A, B, SISTEMA).
    """
    out = []
    if not raw: return out
    
    for parte in raw.split(","):
        parte = parte.strip()
        if not parte: continue
        
        system_tag = 'ANY'
        if ":" in parte:
            tramo, system_tag = parte.split(":", 1)
            system_tag = system_tag.strip().upper()
            parte = tramo.strip()
            
        if "-" in parte:
            a,b = parte.split("-", 1)
            out.append((a.strip(), b.strip(), system_tag))
    return out

# ---------------------------
# PROGRAMA PRINCIPAL
# ---------------------------
def main():
    print("=== Router CDMX: Metro + Metrobús + Trolebús ===")
    origen = input("Estación de origen: ").strip()
    destino = input("Estación de destino: ").strip()

    closed_st_input = input("Estaciones cerradas (separadas por coma, ENTER si ninguna): ").strip()
    estaciones_cerradas = [s.strip() for s in closed_st_input.split(",")] if closed_st_input else []

    closed_segs_raw = input("Tramos cerrados (ej: A-B o A-B:METRO, separados por coma): ").strip()
    tramos_cerrados = parsear_tramos_cerrados(closed_segs_raw)

    try:
        # Optimización: construir_grafo devuelve también el índice
        print("\nCalculando ruta...")
        grafo, indice_nombres = construir_grafo(estaciones_cerradas, tramos_cerrados)
        
        # Optimización: pasar el índice a la búsqueda
        info_ruta = encontrar_ruta_mas_rapida(grafo, indice_nombres, origen, destino)
        
        imprimir_ruta(info_ruta, origen, destino)

    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# Ejecutar main solo si corremos este archivo directamente
if __name__ == "__main__":
    main()
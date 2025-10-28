#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
datos_red_transporte.py

Almacén de datos para el buscador de rutas de CDMX.
Contiene:
 - Parámetros globales (tiempos y tarifas)
 - Listas de estaciones y líneas (Metro, Metrobús, Trolebús)
"""

# ---------------------------
# PARÁMETROS GLOBALES (fáciles de cambiar)
# ---------------------------
# Tiempos promedio entre estaciones por sistema (en minutos)
TIME_METRO = 2.0        # tiempo entre estaciones en Metro
TIME_METROBUS = 3.0     # tiempo entre estaciones en Metrobús
TIME_TROLEBUS = 3.0     # tiempo entre estaciones en Trolebús

# Tiempo extra estimado para hacer transbordo (caminar entre andenes, cambiar entradas)
TRANSFER_PENALTY = 4.0

# Tarifas (pesos mexicanos)
FARE_METRO = 5          # tarifa por entrada al Metro
FARE_METROBUS = 6       # tarifa por entrada al Metrobús
FARE_TROLEBUS = 4       # tarifa por entrada al Trolebús

# Límite para imprimir caminos largos (seguridad)
MAX_DISPLAY = 600

# ---------------------------
# DATOS: LISTAS DE LÍNEAS Y ESTACIONES
# ---------------------------

# LÍNEAS DEL METRO
metro_lines = {
    "L1": ["Observatorio","Tacubaya","Juanacatlán","Chapultepec","Sevilla","Insurgentes",
           "Cuauhtémoc","Balderas","Salto del Agua","Isabel la Católica","Pino Suárez",
           "Merced","Candelaria","San Lázaro","Moctezuma","Balbuena","Boulevard Puerto Aéreo",
           "Gómez Farías","Zaragoza","Pantitlán"],
    "L2": ["Cuatro Caminos","Panteones","Tacuba","Cuitláhuac","Popotla","Colegio Militar",
           "Normal","San Cosme","Revolución","Hidalgo","Bellas Artes","Allende","Zócalo/Tenochtitlan",
           "Pino Suárez","San Antonio Abad","Chabacano","Viaducto","Xola","Villa de Cortés",
           "Nativitas","Portero","Ermita","General Anaya","Tasqueña"],
    "L3": ["Indios Verdes","Deportivo 18 de Marzo","La Raza","Potrero","Autobuses del Norte","Tlatelolco",
           "Guerrero","Hidalgo","Juárez","Balderas","Niños Héroes","Hospital General","Centro Médico",
           "Etiopía/Plaza de la Transparencia","Eugenia","División del Norte","Zapata","Coyoacán",
           "Viveros","Miguel Ángel de Quevedo","Coyoacán (sur)","Copilco","Universidad"],
    "L4": ["Martín Carrera","Talismán","Bondojito","Consulado","Canal del Norte","Morelos",
           "Candelaria","Fray Servando","Jamaica","Santa Anita"],
    "L5": ["Pantitlán","Hangares","Terminal Aérea","Oceanía","Aragón","Eduardo Molina",
           "Consulado","Valle Gómez","La Raza","Autobuses del Norte","Instituto del Petróleo","Politécnico"],
    "L6": ["El Rosario","Tezozómoc","UAM-Azcapotzalco","Ferrería/Arena Ciudad de México","Norte 45",
           "Vallejo","Instituto del Petróleo","Lindavista","Deportivo 18 de Marzo","La Villa-Basílica","Martín Carrera"],
    "L7": ["El Rosario","Aquiles Serdán","Camarones","Refinería","Tacuba","San Joaquín",
           "Polanco","Auditorio","Constituyentes","Tacubaya","San Pedro de los Pinos","San Antonio","Mixcoac","Barranca del Muerto"],
    "L8": ["Garibaldi / Lagunilla","Bellas Artes","San Juan de Letrán","Salto del Agua","Chabacano",
           "Doctores","Obrera","La Viga","Santa Anita","Coyuya","Iztacalco","Apatlaco","Aculco",
           "Escuadrón 201","Atlalilco","Iztapalapa","Cerro de la Estrella","UAM-I","Constitución de 1917"],
    "L9": ["Pantitlán","Puebla","Velódromo","Mixiuhca","Jamaica","Chabacano","Centro Médico","Lázaro Cárdenas","Tacubaya"],
    "L12": ["Tláhuac","Tlaltenco","Zapotitlán","Nopalera","Olivos","Tezonco","Periférico Oriente",
            "Calle 11","Lomas Estrella","San Andrés Tomatlán","Culhuacán","Atlalilco","Mexicaltzingo",
            "Ermita","Parque de los Venados","Eje Central","Zapata","Hospital 20 de Noviembre","Insurgentes Sur","Mixcoac"],
    "LA": ["Pantitlán","Agrícola Oriental","Canal de San Juan","Tepalcates","Guelatao","Peñón Viejo",
           "Acatitla","Santa Marta","Los Reyes","La Paz"],
    "LB": ["Buenavista","Guerrero","Garibaldi/Lagunilla","Morelos","Candelaria","San Lázaro","Gómez Farías",
           "Oceanía","Deportivo Oceanía","Bosque de Aragón","Villa de Aragón","Nezahualcóyotl",
           "Impulsora","Río de los Remedios","Múzquiz","Ecatepec","Olímpica","Plaza Aragón","Ciudad Azteca"]
}

# LÍNEAS DEL METROBÚS
metrobus_lines = {
    "MB1": ["Indios Verdes","Deportivo 18 de Marzo","Potrero","La Raza","Circuito","Buenavista","Revolución",
            "Juárez","Bellas Artes","Cultura","Centro Médico","Chabacano","Eje Central","Term. Chapultepec","Insurgentes"],
    "MB2": ["Tepalcates","Canal de San Juan","General Antonio León","Nicolás Bravo","Constitución de Apatzingán",
            "CCH Oriente","Leyes de Reforma","Del Moral","Río Frío","Rojo Gómez","San Lázaro","Calle 11"],
    "MB3": ["Tenayuca","Progreso Nacional","Potrero","Hidalgo","Juárez","Balderas","Buenavista","La Raza","Deportivo 18 de Marzo",
            "Indios Verdes"],
    "MB4": ["Buenavista","Eje Central","Reforma","Glorieta de Colón","Juárez","Balderas","Obrera","San Antonio Abad","Tepito"],
    "MB5": ["Preparatoria 1","San Lázaro Sur","Río de los Remedios","Vasco de Quiroga","5 de Mayo"],
    "MB6": ["El Rosario","De las Culturas","UAM Azcapotzalco","Norte 45","Ferreria","Vallejo","Instituto del Petróleo","Villa de Aragón"],
    "MB7": ["Indios Verdes","Campo Militar","Campo Marte","Auditorio","Paseo de la Reforma","Glorieta de la Palma","Toreo"]
}

# LÍNEAS DEL TROLEBÚS (versión extendida)
trolebus_lines = {
    "T1": ["Central del Norte","CCH Vallejo","La Raza","Tlatelolco","Garibaldi","Bellas Artes","Centro Histórico","Coyoacán Centro","Terminal del Sur / Tasqueña"],
    "T2": ["CETRAM Chapultepec","Parque México","Hospital General","Mercado Jamaica","Palacio de los Deportes","Velódromo","Foro Sol","CETRAM Pantitlán"],
    "T3": ["Mixcoac","Eje 7 Sur","Museo Transportes","Iztapalapa"],
    "T4": ["Boulevard Puerto Aéreo","Centro Médico","Hidalgo"],
    "T5": ["San Felipe de Jesús","Eje 8 Sur","Hidalgo"],
    "T6": ["El Rosario","Tacubaya","Chapultepec"],
    "T7": ["Periférico Sur / CU","Ciudad Universitaria"],
    "T8": ["San Juan de Aragón","Iztacalco","Constitución de 1917"],
    "T9": ["Villa de Cortés","Apatlaco","Tepalcates"],
    "T12": ["Tasqueña","Céfiro","Tita Avendaño","Cantera","Papatzin","Moctecuzoma","Tepalcatzin","Topiltzin","Iztlizóchitl","Cantil","Eje 10","Pacífico","Circunvalación","Los Pinos","División del Norte","Cerro Huitzilac","Central del Sur","Perisur"],
    "T13": ["Constitución de 1917","Matías Rodríguez","San Felipe de Jesús","UAM-I","Fundición","Mina","Cerro de la Estrella","Sala Quetzalcóatl","Iztapalapa","Puente Titla","Atlalilco","Toltecas","Ermita Iztapalapa","Alhambra","Tokio","Pirineos","Uxmal","Av. Universidad","Gabriel Mancera","Coyoacán","Moras","San Francisco","Las Huertas","Río Churubusco","Galicia","Félix Parra","Goya","Revolución","Mixcoac"]
}
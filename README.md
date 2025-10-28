# CDMX Transit Route Finder

This project is a Python script designed to find the fastest route between two stations in the Mexico City public transportation system, utilizing Dijkstra's algorithm. The finder calculates the optimal path based on estimated travel time, including transfer penalties.

## Features

  * **Fastest Route Calculation:** Finds the route with the lowest total travel time, considering average times between stations and penalties for transfers.
  * **Cost Calculation:** Estimates the total cost of the trip, intelligently applying fares (charging only when entering a new system, not for same-system transfers).
  * **Closure Handling:** Allows the user to dynamically specify stations or line segments that are out of service to exclude them from the search.
  * **Automatic Transfers:** Automatically identifies and calculates the time cost of transfers between different lines and systems that share the same location (based on a normalized station name).

## Supported Systems

The current data model includes the following transit networks:

  * Metro
  * Metrobús
  * Trolebús (Trolleybus)

## How It Works

The `construir_grafo` script first generates a weighted graph of the entire transportation network. In this graph:

  * **Nodes:** Represent a specific station within a line and system (e.g., `(Tacubaya, METRO, L1)`).
  * **Edges (Connections):** Represent the time in minutes to travel between two nodes.
      * Travel between adjacent stations has a defined weight (e.g., `TIME_METRO`).
      * Transfers between nodes with the same name (e.g., `(Balderas, METRO, L3)` and `(Balderas, METROBUS, MB3)`) have a transfer penalty weight (`TRANSFER_PENALTY`).

Subsequently, the `encontrar_ruta_mas_rapida` function uses Dijkstra's algorithm to explore this graph and find the path with the lowest cumulative time from the origin node to the destination node.

## Usage

To use the finder, run the main script from your terminal.

1.  Ensure you have Python 3 installed.

2.  Place both files (`buscador_rutas.py` and `datos_red_transporte.py`) in the same directory.

3.  Run the script:

    ```bash
    python3 buscador_rutas.py
    ```

4.  Follow the prompts in the console:

      * **Estación de origen (Origin station):** Enter the name of the starting station (e.g., `Universidad`).
      * **Estación de destino (Destination station):** Enter the name of the final station (e.g., `El Rosario`).
      * **Estaciones cerradas (Closed stations) (optional):** Enter station names separated by a comma (e.g., `Zocalo, Pino Suarez`). Press Enter if there are none.
      * **Tramos cerrados (Closed segments) (optional):** Enter segments in `StationA-StationB` format, or with a system specified as `StationA-StationB:SYSTEM` (e.g., `Pantitlan-Zaragoza:METRO, Etiopia-Centro Medico`). Press Enter if there are none.

The script will print the optimal route detailed by segments, the total estimated time, and the approximate cost of the trip.

## File Structure

  * `buscador_rutas.py`: Contains the main program logic, including the console interface, graph construction, and the implementation of Dijkstra's algorithm.
  * `datos_red_transporte.py`: Acts as a database and configuration file. It stores all line and station lists, fares, and time parameters (such as transfer penalties and travel times between stations).

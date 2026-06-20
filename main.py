"""
   EXPEDIENTE OVEJA: Y si... No es asi?
Simulación Matemática de Exploración, Navegación y Reconstrucción Vectorial.
Arquitectura: Patrón de Diseño Desacoplado (Modelo-Vista-Controlador simplificado)
Dependencias: Ninguna (Librería estándar de Python exclusivamente)
Matemáticas Aplicadas:
 - Trigonometría Circular (Funciones de Traslación Vectorial en R2)
 - Geometría Analítica Euclidiana (Cálculo de Distancias, Vectores de Dirección)
 - Álgebra Lineal en Sistemas de Coordenadas Acotados (Colisiones y Rebotes)
 - Procesos Estocásticos y Comportamiento Emergente (Eventos Probabilísticos)

Autora: Samantha Villarroel 
Fecha de entrega: 20 - 06 - 2026
"""

import os
import sys
import math
import random
import time

#Comprobación defensiva de la interfaz gráfica Turtle (Tkinter)#
try:
    import turtle
    import tkinter
    HAS_GUI = True
except (ImportError, Exception):
    HAS_GUI = False


# 1. CONFIGURACIÓN Y PALETAS DE COLOR ANSI (TERMINAL)#
class TerminalColor:
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    PURPLE = "\033[35m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

# Constantes del Entorno del Simulador#
LIMIT_MIN = -220
LIMIT_MAX = 220
SAFE_SPAWN_MIN = -180
SAFE_SPAWN_MAX = 180

# Dificultades del simulador#
DIFFICULTY_PARAMS = {
    "Fácil": {
        "step_size": 25.0,
        "event_probability": 0.20,
        "stability_drain": 1.0,
        "corruption_multiplier": 0.8,
        "coherence_gain_multiplier": 1.2
    },
    "Medio": {
        "step_size": 20.0,
        "event_probability": 0.30,
        "stability_drain": 1.5,
        "corruption_multiplier": 1.0,
        "coherence_gain_multiplier": 1.0
    },
    "Difícil": {
        "step_size": 15.0,
        "event_probability": 0.45,
        "stability_drain": 2.5,
        "corruption_multiplier": 1.5,
        "coherence_gain_multiplier": 0.8
    }
}

# 2. MODELO DE DATOS (ESTADO DE LA SONDA Y NODOS DEL MUNDO)#
class WorldNode:
    """Representa un nodo de información, anomalía o núcleo de identidad en el plano 2D."""
    def __init__(self, node_type, name, x, y, description):
        self.node_type = node_type  # PROFU, SIDERALIA, ANDAIRA, NÚCLEO#
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.description = description
        self.decrypted = False      # Indica si el nodo ya ha sido procesado/descifrado#

    def calculate_distance(self, px, py):
        """Calcula la distancia euclidiana entre el nodo y un punto (px, py)."""
        return math.hypot(self.x - px, self.y - py)

    def calculate_bearing(self, px, py):
        """Calcula el rumbo absoluto (ángulo en grados) desde (px, py) hacia este nodo."""
        angle_rad = math.atan2(self.y - py, self.x - px)
        return math.degrees(angle_rad) % 360


class ProbeState:
    """Modelo del estado interno de la sonda O.V.E.J.A."""
    def __init__(self, mission_name, start_x, start_y, start_angle, difficulty):
        self.mission_name = mission_name
        self.x = float(start_x)
        self.y = float(start_y)
        self.start_x = float(start_x)
        self.start_y = float(start_y)

        self.angle = float(start_angle % 360)
        self.initial_angle = float(start_angle % 360)

        self.difficulty = difficulty
        # Parámetros mecánicos según dificultad#
        self.params = DIFFICULTY_PARAMS.get(difficulty, DIFFICULTY_PARAMS["Medio"])
        
        # Variables principales dinámicas#
        self.stability = 100.0  # Capacidad operativa y energética (0 - 100)#
        self.corruption = 0.0   # Ruido electromagnético y distorsión de datos (0 - 100)#
        self.coherence = 30.0   # Integridad de datos lógicos de memoria (0 - 100)#
        self.steps = 0          # Contador de acciones operativas principales#
        
        # Historial de eventos y evidencias encontradas#
        self.logs = []
        self.decrypted_nodes = []  # Nodos resueltos con éxito#
        self.score = 0
        self.rank = "D"
        self.termination_cause = "Simulación activa"

    def add_log(self, message):
        """Añade una entrada al historial con el paso actual."""
        entry = f"Paso {self.steps:02d}: {message}"
        self.logs.append(entry)

    def update_stats(self, d_stability, d_corruption, d_coherence):
        """Aplica cambios delta a las variables de forma segura y acotada."""
        self.stability = max(0.0, min(100.0, self.stability + d_stability))
        self.corruption = max(0.0, min(100.0, self.corruption + d_corruption))
        self.coherence = max(0.0, min(100.0, self.coherence + d_coherence))

    def evaluate_status(self):
        """Evalúa si se han alcanzado condiciones de terminación crítica."""
        if self.stability <= 0.0:
            self.termination_cause = "Colapso Estructural de Estabilidad (Integridad 0%)"
            return "COLLAPSE"
        if self.corruption >= 100.0:
            self.termination_cause = "Corrupción de Código y Desbordamiento de Memoria (100%)"
            return "CORRUPTED"
        return "ACTIVE"

# 3. RENDERIZADO GRÁFICO (TURTLE ENGINE VISUALIZER)#
class TurtleVisualizer:
    """Módulo gráfico para la visualización elegante de la simulación en tiempo real."""
    def __init__(self):
        self.screen = None
        self.bg_drawer = None
        self.node_drawer = None
        self.path_drawer = None
        self.oveja_turtle = None
        self.hud_drawer = None
        self.radar_drawer = None

    def initialize(self):
        """Configura el entorno de la ventana Turtle y la paleta retro-futurista."""
        global HAS_GUI
        if not HAS_GUI:
            return False
        
        try:
            # Configuración de ventana principal
            self.screen = turtle.Screen()
            self.screen.setup(width=920, height=620)
            self.screen.title("EXPEDIENTE OVEJA (VISUAL MAP)")
            self.screen.bgcolor("#0B0F19")  # Fondo azul oscuro/negro#
            self.screen.tracer(0, 0)         # Desactivar refresco automático para optimizar#
            
            # Inicializar pinceles para diferentes capas#
            self.bg_drawer = turtle.Turtle()
            self.bg_drawer.hideturtle()
            self.bg_drawer.speed(0)
            
            self.node_drawer = turtle.Turtle()
            self.node_drawer.hideturtle()
            self.node_drawer.speed(0)
            
            self.path_drawer = turtle.Turtle()
            self.path_drawer.hideturtle()
            self.path_drawer.speed(0)
            self.path_drawer.pensize(2)
            self.path_drawer.color("#38BDF8")  # Estela cian brillante#
            
            self.hud_drawer = turtle.Turtle()
            self.hud_drawer.hideturtle()
            self.hud_drawer.speed(0)
            
            self.radar_drawer = turtle.Turtle()
            self.radar_drawer.hideturtle()
            self.radar_drawer.speed(0)
            
            self.oveja_turtle = turtle.Turtle()
            self.oveja_turtle.shape("triangle")
            self.oveja_turtle.shapesize(stretch_wid=1.0, stretch_len=1.3)
            self.oveja_turtle.color("#38BDF8")  # Color de la sonda#
        
            self.oveja_turtle.penup()
            
            return True
        except Exception:
            HAS_GUI = False
            return False

    def draw_boundaries_and_grid(self):
        """Dibuja los límites lógicos (-220 a 220) y la rejilla cartesiana en Turtle."""
        if not HAS_GUI:
            return
        
        t = self.bg_drawer
        t.clear()
        
        # 1. Caja del límite lógico de la simulación (-220 a 220)#
        t.penup()
        t.color("#1E293B")  # Slate-800#
        t.pensize(3)
        t.goto(LIMIT_MIN, LIMIT_MIN)
        t.pendown()
        for _ in range(4):
            t.forward(LIMIT_MAX - LIMIT_MIN)
            t.left(90)
            
        # 2. Marco exterior estético#
        t.penup()
        t.color("#334155")  # Slate-700
        t.pensize(1)
        t.goto(LIMIT_MIN - 6, LIMIT_MIN - 6)
        t.pendown()
        for _ in range(4):
            t.forward((LIMIT_MAX - LIMIT_MIN) + 12)
            t.left(90)
            
        # 3. Líneas de guía de la rejilla (cada 100 unidades)#
        t.color("#1E293B")
        for val in [-100, 0, 100]:
            # Rejilla vertical
            t.penup()
            t.goto(val, LIMIT_MIN)
            t.pendown()
            t.goto(val, LIMIT_MAX)
            # Rejilla horizontal
            t.penup()
            t.goto(LIMIT_MIN, val)
            t.pendown()
            t.goto(LIMIT_MAX, val)
            
        # 4. Etiquetas numéricas de coordenadas#
        t.penup()
        t.color("#64748B")  # Slate-500
        for val in [-200, -100, 0, 100, 200]:
            # Eje X#
            t.goto(val, LIMIT_MIN - 20)
            t.write(str(val), align="center", font=("Courier", 8, "bold"))
            # Eje Y#
            t.goto(LIMIT_MIN - 28, val - 4)
            t.write(str(val), align="right", font=("Courier", 8, "bold"))
            
        # 5. Línea divisoria vertical de la interfaz lateral (Sidebar HUD)#
        t.penup()
        t.color("#334155")
        t.pensize(2)
        t.goto(240, -250)
        t.pendown()
        t.goto(240, 250)
        
        self.screen.update()

    def draw_nodes(self, nodes):
        """Dibuja los nodos especiales distribuidos en la simulación."""
        if not HAS_GUI:
            return
        
        t = self.node_drawer
        t.clear()
        
        for node in nodes:
            t.penup()
            t.goto(node.x, node.y)
            
            if node.node_type == "PROFU":
                # Emerald / Cyan - Fragmentos de datos profu#
                color = "#10B981" if not node.decrypted else "#334155"
                t.color(color)
                t.goto(node.x, node.y - 6)
                t.pendown()
                t.circle(6)
                t.penup()
                t.goto(node.x, node.y - 2)
                t.pendown()
                t.begin_fill()
                t.circle(2)
                t.end_fill()
                
            elif node.node_type == "SIDERALIA":
                # Purple - Faros de estabilidad#
                color = "#A855F7" if not node.decrypted else "#334155"
                t.color(color)
                t.goto(node.x - 5, node.y)
                t.pendown()
                t.begin_fill()
                for _ in range(4):
                    t.forward(10)
                    t.left(90)
                t.end_fill()
                
            elif node.node_type == "ANDAIRA":
                # Crimson Red - Anomalía distorsionadora (siempre activa)#
                t.color("#EF4444")
                t.pensize(2)
                t.pendown()
                t.goto(node.x - 6, node.y - 6)
                t.goto(node.x + 6, node.y + 6)
                t.penup()
                t.goto(node.x + 6, node.y - 6)
                t.pendown()
                t.goto(node.x - 6, node.y + 6)
                t.penup()
                t.pensize(1)
                
            elif node.node_type == "NÚCLEO":
                # Gold/Amber - Identidad central#
                color = "#F59E0B" if not node.decrypted else "#334155"
                t.color(color)
                t.goto(node.x, node.y - 4)
                t.pendown()
                t.circle(4)
                t.penup()
                t.goto(node.x, node.y - 9)
                t.pendown()
                t.circle(9)
                
            t.penup()
            # Etiquetado en tamaño reducido por encima del nodo#
            t.color("#94A3B8" if not node.decrypted else "#475569")
            t.goto(node.x, node.y + 10)
            tag = node.name if not node.decrypted else f"{node.name} (DEC)"
            t.write(tag, align="center", font=("Courier", 7, "normal"))
            
        self.screen.update()

    def update_probe_trail(self, start_x, start_y, px, py, angle):
        """Actualiza el trazado del recorrido histórico y la posición de OVEJA."""
        if not HAS_GUI:
            return
        
        # Dibujar marcador de origen en el primer movimiento#
        if self.path_drawer.undobufferentries() == 0:
            self.path_drawer.penup()
            self.path_drawer.goto(start_x, start_y)
            self.path_drawer.pendown()
            
            # Dibujar un pequeño anillo de partida en el fondo#
            t = self.bg_drawer
            t.penup()
            t.color("#64748B")
            t.goto(start_x, start_y - 4)
            t.pendown()
            t.circle(4)
            t.penup()
            
        # Extender el trazado de la ruta activa#
        self.path_drawer.goto(px, py)
        
        # Reposicionar el puntero gráfico de OVEJA#
        self.oveja_turtle.goto(px, py)
        self.oveja_turtle.setheading(angle)
        
        self.screen.update()

    def draw_hud(self, state):
        """Actualiza el panel textual lateral HUD en Turtle (sidebar derecha)."""
        if not HAS_GUI:
            return
        
        t = self.hud_drawer
        t.clear()
        
        start_x = 260
        
        # Cabecera principal#
        t.penup()
        t.color("#F59E0B")  # Ámbar#
        t.goto(start_x, 220)
        t.write("EXPEDIENTE OVEJA", align="left", font=("Courier", 13, "bold"))
        
        t.color("#06B6D4")  # Cian#
        t.goto(start_x, 202)
        t.write("CORE TELEMETRY PANEL", align="left", font=("Courier", 9, "bold"))
        
        # Divisor#
        t.color("#334155")
        t.goto(start_x, 192)
        t.write("==========================", align="left", font=("Courier", 9, "normal"))
        
        # Parámetros del Expediente#
        t.color("#E2E8F0")
        t.goto(start_x, 172)
        t.write(f"Misión: {state.mission_name[:15]}", align="left", font=("Courier", 9, "bold"))
        t.goto(start_x, 154)
        t.write(f"Dificultad: {state.difficulty.upper()}", align="left", font=("Courier", 9, "normal"))
        t.goto(start_x, 136)
        t.write(f"Ciclo / Paso: {state.steps}", align="left", font=("Courier", 9, "normal"))
        
        # Barras de estado
        # 1. ESTABILIDAD
        t.goto(start_x, 106)
        stab_col = "#EF4444" if state.stability < 30 else "#E2E8F0"
        t.color(stab_col)
        t.write(f"ESTABILIDAD: {state.stability:.1f}%", align="left", font=("Courier", 9, "bold"))
        
        t.goto(start_x, 92)
        bar_stab = "█" * int(state.stability / 10) + "░" * (10 - int(state.stability / 10))
        t.write(f"[{bar_stab}]", align="left", font=("Courier", 9, "normal"))
        
        # 2. CORRUPCIÓN
        t.goto(start_x, 68)
        corr_col = "#EF4444" if state.corruption > 60 else "#E2E8F0"
        t.color(corr_col)
        t.write(f"CORRUPCIÓN : {state.corruption:.1f}%", align="left", font=("Courier", 9, "bold"))
        
        t.goto(start_x, 54)
        bar_corr = "█" * int(state.corruption / 10) + "░" * (10 - int(state.corruption / 10))
        t.write(f"[{bar_corr}]", align="left", font=("Courier", 9, "normal"))
        
        # 3. COHERENCIA
        t.goto(start_x, 30)
        coh_col = "#10B981" if state.coherence >= 80 else "#E2E8F0"
        t.color(coh_col)
        t.write(f"COHERENCIA : {state.coherence:.1f}%", align="left", font=("Courier", 9, "bold"))
        
        t.goto(start_x, 16)
        bar_coh = "█" * int(state.coherence / 10) + "░" * (10 - int(state.coherence / 10))
        t.write(f"[{bar_coh}]", align="left", font=("Courier", 9, "normal"))
        
        # Divisor secundario
        t.color("#334155")
        t.goto(start_x, 2)
        t.write("--------------------------", align="left", font=("Courier", 9, "normal"))
        
        # Posicionamiento Vectorial
        t.color("#94A3B8")
        t.goto(start_x, -16)
        t.write(f"Coordenada X: {state.x:6.2f} u", align="left", font=("Courier", 8, "normal"))
        t.goto(start_x, -30)
        t.write(f"Coordenada Y: {state.y:6.2f} u", align="left", font=("Courier", 8, "normal"))
        t.goto(start_x, -44)
        t.write(f"Ángulo Rumbo: {state.angle:6.1f}°", align="left", font=("Courier", 8, "normal"))
        
        # Evidencias descifradas
        t.color("#10B981")
        t.goto(start_x, -68)
        t.write(f"EVIDENCIAS DESCIFRADAS: {len(state.decrypted_nodes)}", align="left", font=("Courier", 8, "bold"))
        
        # Divisor terciario
        t.color("#334155")
        t.goto(start_x, -82)
        t.write("--------------------------", align="left", font=("Courier", 9, "normal"))
        
        # Log de eventos
        t.color("#94A3B8")
        t.goto(start_x, -98)
        t.write("Último suceso de bitácora:", align="left", font=("Courier", 8, "underline"))
        
        last_log = state.logs[-1] if state.logs else "Conexión satelital iniciada."
        # Truncar log para que encaje visualmente en el sidebar
        if len(last_log) > 28:
            last_log = last_log[:25] + "..."
            
        t.color("#38BDF8")
        t.goto(start_x, -114)
        t.write(last_log, align="left", font=("Courier", 7, "italic"))
        
        # Indicador de estado del Core
        status_txt = "INTEGRO"
        status_col = "#10B981"
        if state.stability < 30:
            status_txt = "ALERTA DAÑO"
            status_col = "#F97316"
        if state.corruption > 50:
            status_txt = "RUIDO ELEVADO"
            status_col = "#EF4444"
        if state.stability < 15:
            status_txt = "S.O.S. COLAPSO"
            status_col = "#EF4444"
            
        t.color(status_col)
        t.goto(start_x, -145)
        t.write(f"ESTADO GENERAL: {status_txt}", align="left", font=("Courier", 9, "bold"))
        
        self.screen.update()

    def trigger_radar_sweep_animation(self, px, py):
        """Efecto visual interactivo de barrido de radar expansivo en Turtle."""
        if not HAS_GUI:
            return
        
        t = self.radar_drawer
        t.pensize(1)
        
        # Simular onda expansiva circular en 4 etapas#
        for r in [20, 50, 90, 130]:
            t.clear()
            t.penup()
            t.goto(px, py - r)
            t.color("#06B6D4")  # Cian brillante#
            t.pendown()
            t.circle(r)
            self.screen.update()
            time.sleep(0.04)
            
        # Limpiar rastro de radar#
        t.clear()
        self.screen.update()

# 4. MOTOR DE EVENTOS ALEATORIOS (SISTEMA VIVO COMPORTAMIENTO EMERGENTE)#
class EventEngine:
    """Administrador estocástico de incidencias meteorológicas cuánticas y fluctuaciones del sistema."""
    def evaluate_chance(state):
        """Determina de manera probabilística si ocurre un evento durante el movimiento."""
        prob = state.params["event_probability"]
        return random.random() < prob
    def trigger_event(state):
        """Selecciona y ejecuta uno de los 6 eventos lógicos integrados, aplicando efectos reales."""
        events = [
            # Evento 1: Corriente de Deriva Cuántica (Hazard de movimiento)#
            {
                "name": "Corriente de Deriva Vectorial",
                "color": TerminalColor.RED,
                "msg": "Una turbulencia en el campo de Higgs empuja y altera el rumbo de la sonda.",
                "action": EventEngine._apply_drift
            },
            # Evento 2: Interferencia Electromagnética#
            {
                "name": "Interferencia Cuántica Intensa",
                "color": TerminalColor.RED,
                "msg": "Fuerte tormenta de ruido satura los búferes. Aumento de ruido de bits.",
                "action": EventEngine._apply_interference
            },
            # Evento 3: Eco de Datos del Pasado (Benigno)#
            {
                "name": "Eco del Expediente Original",
                "color": TerminalColor.GREEN,
                "msg": "Una resonancia residual de la memoria original del sistema es reordenada.",
                "action": EventEngine._apply_echo
            },
            # Evento 4: Fallo Crítico de Subsistemas
            {
                "name": "Fallo de Subsistemas de Alimentación",
                "color": TerminalColor.RED,
                "msg": "Un cortocircuito transitorio drena carga acumulada de los capacitores.",
                "action": EventEngine._apply_system_glitch
            },
            # Evento 5: Distorsión del Mapa Topológico#
            {
                "name": "Fluctuación Topológica de Anomalías",
                "color": TerminalColor.PURPLE,
                "msg": "Un cambio cuántico altera la geometría espacial de las anomalías ANDAIRA.",
                "action": EventEngine._apply_matrix_distortion
            },
            # Evento 6: Bucle de Autoreparación Secundario (Favorable)
            {
                "name": "Bucle de Autoconsistencia Operativa",
                "color": TerminalColor.GREEN,
                "msg": "Los hilos lógicos en desuso se desfragmentan, restaurando estabilidad.",
                "action": EventEngine._apply_recovery
            }
        ]
        
        event = random.choice(events)
        state.steps += 1
        state.add_log(f"INCIDENCIA: {event['name']}")
        
        # Ejecutar acción mutadora del estado#
        log_feedback = event["action"](state)
        
        # Retornar datos detallados para la interfaz CLI#
        return {
            "name": event["name"],
            "color": event["color"],
            "msg": event["msg"],
            "feedback": log_feedback
        }

    # Métodos privados de alteración de estados#
    def _apply_drift(state):
        drift_angle = random.uniform(-40, 40)
        drift_dist = random.uniform(10, 25)
        
        # Modificar ángulo rumbo de la sonda#
        state.angle = (state.angle + drift_angle) % 360
        
        # Mover sonda#
        rad = math.radians(state.angle)
        dx = math.cos(rad) * drift_dist
        dy = math.sin(rad) * drift_dist
        
        # Validar y acotar nueva posición#
        state.x = max(LIMIT_MIN, min(LIMIT_MAX, state.x + dx))
        state.y = max(LIMIT_MIN, min(LIMIT_MAX, state.y + dy))
        
        # Impacto a estadísticas#
        loss = state.params["stability_drain"] * 3
        state.update_stats(-loss, 8 * state.params["corruption_multiplier"], 0)
        
        return f"Desplazamiento angular: {drift_angle:+.1f}°. Deriva espacial: {drift_dist:.1f}u. Estabilidad: -{loss:.1f}%."

    @staticmethod
    def _apply_interference(state):
        corr_inc = 15.0 * state.params["corruption_multiplier"]
        state.update_stats(0, corr_inc, -5.0)
        return f"Corrupción incrementada: +{corr_inc:.1f}%. Coherencia degradada: -5.0%."

    @staticmethod
    def _apply_echo(state):
        coh_inc = 12.0 * state.params["coherence_gain_multiplier"]
        state.update_stats(2.0, -5.0, coh_inc)
        return f"Coherencia restaurada: +{coh_inc:.1f}%. Corrupción reducida: -5.0%."

    @staticmethod
    def _apply_system_glitch(state):
        loss = state.params["stability_drain"] * 5
        state.update_stats(-loss, 5.0, -8.0)
        return f"Estabilidad reducida drásticamente: -{loss:.1f}%. Coherencia del núcleo: -8.0%."

    @staticmethod
    def _apply_matrix_distortion(state):
        state.update_stats(0, 10.0 * state.params["corruption_multiplier"], 0)
        # Señalizar que las anomalías ANDAIRA deben reubicarse (el motor de simulación lo gestionará)#
        return "Se detecta teletransportación de anomalías ANDAIRA por refracción de vacío. Corrupción +10.0%."

    @staticmethod
    def _apply_recovery(state):
        state.update_stats(15.0, -10.0, 5.0)
        return "Mantenimiento automatizado completo. Estabilidad: +15.0%. Corrupción: -10.0%."

# 5. CORE ENGINE (SISTEMA DE SIMULACIÓN PRINCIPAL)#
class SimulationEngine:
    """Motor de simulación y física vectorial del proyecto Expediente Oveja."""
    def __init__(self, state):
        self.state = state
        self.nodes = []
        self._spawn_world_elements()

    def _spawn_world_elements(self):
        """Distribuye estratégicamente los elementos del mundo en el espacio acotado."""
        # Colocación segura basada en la posición de inicio#
        px, py = self.state.x, self.state.y
        
        # 1. PROFU (Nodos de información - Verde/Azul) - Se colocan 3 nodos#
        self.nodes.append(WorldNode("PROFU", "P-ALPHA", 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     "Registros de bitácora iniciales de colisión."))
        self.nodes.append(WorldNode("PROFU", "P-BETA", 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     "Espectrografía analítica del objeto desconocido."))
        self.nodes.append(WorldNode("PROFU", "P-GAMMA", 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     "Archivos del manifiesto de tripulación original."))

        # 2. SIDERALIA (Nodos de estabilización - Morado) - Se colocan 2 nodos
        self.nodes.append(WorldNode("SIDERALIA", "S-VORTEX", 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     "Ancla magnética funcional de recarga de batería."))
        self.nodes.append(WorldNode("SIDERALIA", "S-HELIX", 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                     "Punto de restauración de caché estructural."))

        # 3. ANDAIRA (Nodos de peligro de corrupción - Rojo) - Se colocan 4 nodos#
        for i, name in enumerate(["A-NEXUS", "A-STORM", "A-CORRUPT", "A-VOID"]):
            self.nodes.append(WorldNode("ANDAIRA", name, 
                                         random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                         random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX), 
                                         f"Anomalía electromagnética distorsionadora {i+1}."))

        # 4. NÚCLEO (Nodo Final - Amarillo)#
        # Se requiere que el Núcleo esté a una distancia segura (>160u) para asegurar exploración real#
        while True:
            core_x = random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX)
            core_y = random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX)
            dist = math.hypot(core_x - px, core_y - py)
            if dist >= 160.0:
                self.nodes.append(WorldNode("NÚCLEO", "CORE_N", core_x, core_y, 
                                             "Cámara del Núcleo de Identidad e Inteligencia."))
                break

    def relocate_andaira_nodes(self):
        """Reubica de manera estocástica las anomalías de corrupción (comportamiento emergente)."""
        for node in self.nodes:
            if node.node_type == "ANDAIRA":
                node.x = random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX)
                node.y = random.uniform(SAFE_SPAWN_MIN, SAFE_SPAWN_MAX)

    def advance_probe(self):
        """Realiza el movimiento de la sonda en R2 aplicando trigonometría analítica."""
        self.state.steps += 1
        
        # Conversión matemática angular: Grados sexagesimales a Radianes#
        angle_rad = math.radians(self.state.angle)
        
        # Vector dirección trigonométrico unitario multiplicado por el paso operativo#
        dx = math.cos(angle_rad) * self.state.params["step_size"]
        dy = math.sin(angle_rad) * self.state.params["step_size"]
        
        target_x = self.state.x + dx
        target_y = self.state.y + dy
        
        # Control geométrico de límites del mundo#
        collision_border = False
        if target_x < LIMIT_MIN or target_x > LIMIT_MAX or target_y < LIMIT_MIN or target_y > LIMIT_MAX:
            collision_border = True
            
        if collision_border:
            # Acción correctiva: Bloqueo de avance, rebotar o retrotraer con penalización de daño#
            self.state.update_stats(-10.0, 8.0, 0)
            self.state.add_log("COLISIÓN: Transgresión de frontera del mapa geométrico.")
            
            # Retroceder la trayectoria ligeramente para no quedar atascado#
            self.state.x = max(LIMIT_MIN + 5, min(LIMIT_MAX - 5, self.state.x))
            self.state.y = max(LIMIT_MIN + 5, min(LIMIT_MAX - 5, self.state.y))
            
            return {
                "success": False,
                "msg": "ERROR CRÍTICO: La sonda ha chocado con la frontera vectorial del plano lógigo. El sistema retrocedió.",
                "stability_impact": -10.0,
                "corruption_impact": +8.0
            }
        else:
            # Actualización del vector de coordenadas#
            self.state.x = target_x
            self.state.y = target_y
            
            # Consumo metabólico de estabilidad por movimiento#
            drain = self.state.params["stability_drain"]
            self.state.update_stats(-drain, 0, 0)
            self.state.add_log(f"Movimiento hacia ({self.state.x:.1f}, {self.state.y:.1f})")
            
            # Comprobaciones de colisiones/proximidad con los nodos del mapa#
            proximity_feedback = self._check_node_proximity()
            
            return {
                "success": True,
                "msg": f"Avance exitoso. Nueva posición: ({self.state.x:.2f}, {self.state.y:.2f}).",
                "stability_impact": -drain,
                "corruption_impact": 0,
                "proximity_feedback": proximity_feedback
            }

    def turn_probe(self, direction, degrees_val):
        """Modifica el rumbo de la sonda en base a giros a izquierda o derecha."""
        self.state.steps += 1
        
        # Aplicar el cambio angular matemático#
        if direction == "LEFT":
            self.state.angle = (self.state.angle + degrees_val) % 360
            self.state.add_log(f"Giro Izq: +{degrees_val}° rumbo ajustado a {self.state.angle:.1f}°")
        elif direction == "RIGHT":
            self.state.angle = (self.state.angle - degrees_val) % 360
            self.state.add_log(f"Giro Der: -{degrees_val}° rumbo ajustado a {self.state.angle:.1f}°")
            
        # El ajuste de actitud consume mínima potencia estructural#
        self.state.update_stats(-0.5, 0, 0)
        
        return f"Sonda reorientada. Nuevo ángulo de navegación: {self.state.angle:.1f}°."

    def execute_active_scan(self):
        """Lanza un pulso electromagnético calculando distancias y vectores a los nodos."""
        self.state.steps += 1
        self.state.update_stats(-2.0, 1.0, 0)  # Consumo energético por barrido activo
        self.state.add_log("Barrido de radar espectral activo realizado.")
        
        scan_results = []
        for node in self.nodes:
            dist = node.calculate_distance(self.state.x, self.state.y)
            bearing = node.calculate_bearing(self.state.x, self.state.y)
            
            # Rumbo relativo al ángulo actual de la sonda OVEJA#
            relative_bearing = (bearing - self.state.angle) % 360
            
            # Clasificación analógica de dirección relativa#
            if 315 <= relative_bearing or relative_bearing < 45:
                direction_str = "Proa (Frente)"
            elif 45 <= relative_bearing < 135:
                direction_str = "Babor (Izquierda)"
            elif 135 <= relative_bearing < 225:
                direction_str = "Popa (Atrás)"
            else:
                direction_str = "Estribor (Derecha)"
                
            scan_results.append({
                "node": node,
                "distance": dist,
                "direction": direction_str,
                "bearing": bearing
            })
            
        # Ordenar por proximidad Euclidiana#
        scan_results.sort(key=lambda item: item["distance"])
        return scan_results

    def interpret_system_diagnostics(self):
        """Permite realinear variables internas de coherencia reduciendo estabilidad."""
        self.state.steps += 1
        
        # Realineación selectiva de lógica#
        stability_cost = 10.0
        coherence_heal = 12.0 * self.state.params["coherence_gain_multiplier"]
        
        self.state.update_stats(-stability_cost, -8.0, coherence_heal)
        self.state.add_log("Alineación del sistema y recalibración de variables efectuada.")
        
        return {
            "stability_cost": stability_cost,
            "coherence_gain": coherence_heal,
            "corruption_loss": 8.0
        }

    def _check_node_proximity(self):
        """Verifica de forma proactiva si la sonda interactúa con nodos del plano 2D."""
        feedback = []
        px, py = self.state.x, self.state.y
        
        for node in self.nodes:
            if node.decrypted and node.node_type != "ANDAIRA":
                continue
                
            dist = node.calculate_distance(px, py)
            
            # Radios de acoplamiento diferencial#
            # 1. Colisión con anomalía ANDAIRA (Rojo) - Radio < 25#
            if node.node_type == "ANDAIRA" and dist <= 25.0:
                corr_inc = 20.0 * self.state.params["corruption_multiplier"]
                damage = self.state.params["stability_drain"] * 6
                self.state.update_stats(-damage, corr_inc, -10)
                
                msg = f"¡ALERTA DE ANOMALÍA! Colisión de proximidad con anomalía {node.name}. Corrupción +{corr_inc:.1f}%, Estabilidad -{damage:.1f}%."
                self.state.add_log(f"DAÑO: Colisión anomalía {node.name}")
                feedback.append({"type": "ANDAIRA", "msg": msg, "node": node})
                
            # 2. Reconstrucción de fragmento PROFU (Verde) - Radio < 20#
            elif node.node_type == "PROFU" and dist <= 20.0 and not node.decrypted:
                coh_inc = 22.0 * self.state.params["coherence_gain_multiplier"]
                node.decrypted = True
                self.state.decrypted_nodes.append(node)
                self.state.update_stats(5.0, -10.0, coh_inc)
                
                msg = f"¡DATOS DETECTADOS! Fragmento {node.name} recuperado y cargado en el búfer. Coherencia +{coh_inc:.1f}%, Corrupción -10.0%."
                self.state.add_log(f"DESCIFRADO: Fragmento de datos {node.name}")
                feedback.append({"type": "PROFU", "msg": msg, "node": node})
                
            # 3. Descarga de anclaje SIDERALIA (Morado) - Radio < 20#
            elif node.node_type == "SIDERALIA" and dist <= 20.0 and not node.decrypted:
                node.decrypted = True
                self.state.decrypted_nodes.append(node)
                self.state.update_stats(25.0, -5.0, 8.0)
                
                msg = f"¡ANCLA ALCANZADA! Nodo de estabilización {node.name} activado. Estabilidad +25.0%, Coherencia +8.0%."
                self.state.add_log(f"CONEXIÓN: Faro estabilizador {node.name}")
                feedback.append({"type": "SIDERALIA", "msg": msg, "node": node})
                
            # 4. Acoplamiento al NÚCLEO CENTRAL (Amarillo) - Radio < 20#
            elif node.node_type == "NÚCLEO" and dist <= 20.0:
                # El juego detectará el fin por acoplamiento del núcleo#
                feedback.append({"type": "NÚCLEO", "msg": "Señal portadora del NÚCLEO detectada a menos de 20u de distancia. ¡Fusión lista!", "node": node})
                
        return feedback

    def calculate_final_puntuaction(self):
        """Calcula el puntaje final estructurado y asigna un ranking oficial de desempeño."""
        evidences_count = len([n for n in self.state.decrypted_nodes if n.node_type == "PROFU"])
        siderailas_count = len([n for n in self.state.decrypted_nodes if n.node_type == "SIDERALIA"])
        
        # Pesos matemáticos de la fórmula#
        score = (evidences_count * 1200) + (siderailas_count * 600)
        score += (self.state.stability * 25) + (self.state.coherence * 35)
        score -= (self.state.corruption * 30)
        score -= (self.state.steps * 15)
        
        # Ajustes de bonificación por nivel de complejidad seleccionado#
        diff_multiplier = 1.0
        if self.state.difficulty == "Medio":
            diff_multiplier = 1.4
        elif self.state.difficulty == "Difícil":
            diff_multiplier = 2.0
            
        score = int(score * diff_multiplier)
        self.state.score = max(0, score)
        
        # Tabulación y asignación de rangos#
        if self.state.score >= 5500:
            self.state.rank = "S"
        elif self.state.score >= 4000:
            self.state.rank = "A"
        elif self.state.score >= 2500:
            self.state.rank = "B"
        elif self.state.score >= 1200:
            self.state.rank = "C"
        else:
            self.state.rank = "D"

# 6. VISTAS DEL SISTEMA (CONSOLA CLI Y DIAGRAMACIÓN ASCII)#
class TerminalView:
    """Consola CLI para proyectar textos informativos, telemetría y diagnósticos."""
    @staticmethod
    def type_text(text, delay=0.015, color=None):
        """Imprime texto con efecto mecanografiado para simular interfaz antigua."""
        if color:
            sys.stdout.write(color)
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        if color:
            sys.stdout.write(TerminalColor.RESET)
        sys.stdout.write("\n")

    @staticmethod
    def show_boot_loader():
        """Secuencia de arranque militar tecnológica para sumergir al jurado en la simulación."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{TerminalColor.GRAY}  {TerminalColor.RESET}")
        TerminalView.type_text(" [SISTEMA] INICIANDO CARGADOR DE MEMORIA ENLACE CORE v3.11...", 0.01, TerminalColor.CYAN)
        time.sleep(0.1)
        TerminalView.type_text(" [SISTEMA] INTEGRIDAD DE MEMORIA MATEMÁTICA: COMPROBADA", 0.008, TerminalColor.GREEN)
        TerminalView.type_text(" [SISTEMA] CALIBRANDO COMPÁS ARCTANGENTE DEL VECTOR PLANAR...", 0.008, TerminalColor.GREEN)
        TerminalView.type_text(" [SISTEMA] ESTABLECIENDO CONEXIÓN TELEDIRIGIDA DE SONDA O.V.E.J.A...", 0.01, TerminalColor.CYAN)
        print(f"{TerminalColor.GRAY}   {TerminalColor.RESET}")
        time.sleep(0.4)
        
        banner = f"""{TerminalColor.CYAN}{TerminalColor.BOLD}
 ███████╗██╗  ██╗██████╗ ███████╗██████╗ ██╗███████╗███╗   ██╗████████╗███████╗
 ██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██╔══██╗██║██╔════╝████╗  ██║╚══██╔══╝██╔════╝
 █████╗   ╚███╔╝ ██████╔╝█████╗  ██║  ██║██║█████╗  ██╔██╗ ██║   ██║   █████╗  
 ██╔══╝   ██╔██╗ ██╔═══╝ ██╔══╝  ██║  ██║██║██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  
 ███████╗██╔╝ ██╗██║     ███████╗██████╔╝██║███████╗██║ ╚████║   ██║   ███████╗
 ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═════╝ ╚═╝╚══════╝╚═╝  ╚═════╝   ╚═╝   ╚══════╝
                            {TerminalColor.PURPLE}██████╗ ██╗   ██╗███████╗█████████ ╗ █████╗ {TerminalColor.CYAN}
                           {TerminalColor.PURPLE}██╔═══██╗██║   ██║██╔════╝╚══╗██ ╔══╝██╔══██╗{TerminalColor.CYAN}
                           {TerminalColor.PURPLE}██║   ██║██║   ██║█████╗     ║██ ║   ███████║{TerminalColor.CYAN}
                           {TerminalColor.PURPLE}██║   ██║╚██╗ ██╔╝██╔══╝  ██ ║██ ║   ██╔══██║{TerminalColor.CYAN}
                           {TerminalColor.PURPLE}╚██████╔╝ ╚████╔╝ ███████╗██████ ║   ██║  ██║{TerminalColor.CYAN}
                            {TerminalColor.PURPLE}╚═════╝   ╚═══╝  ╚══════╝╚══════╝   ╚═╝  ╚═╝{TerminalColor.RESET}
            {TerminalColor.YELLOW}-- INFORME EXPEDIENTAL DE EXPLORACIÓN VECTORIAL --{TerminalColor.RESET}
        """
        print(banner)
        time.sleep(0.5)

    @staticmethod
    def show_menu():
        """Despliega las opciones del panel principal."""
        print(f"\n{TerminalColor.BOLD}{TerminalColor.CYAN}  MENU OPERATIVO DE ACCESO LÓGICO:{TerminalColor.RESET}")
        print(f"  {TerminalColor.GREEN}1. Nueva simulación de expediente{TerminalColor.RESET}")
        print(f"  {TerminalColor.CYAN}2. Manual de operación (Cómo jugar){TerminalColor.RESET}")
        print(f"  {TerminalColor.PURPLE}3. Detalles de investigación (Arquitectura){TerminalColor.RESET}")
        print(f"  {TerminalColor.RED}4. Desconectar terminal (Salir){TerminalColor.RESET}")
        print()

    @staticmethod
    def render_ascii_minimap(state, nodes):
        """Renderiza un mapa ASCII representativo en consola para asegurar portabilidad."""
        # Se genera una cuadrícula estática de 11x11 caracteres representativos#
        # Cada caracter representa un bloque espacial de 40u x 40u del mundo real#
        grid_size = 11
        half_grid = grid_size // 2
        block_scale = 40.0
        
        # Inicializar el tapiz del plano con caracteres vacíos#
        matrix = [[" · " for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Posicionar Nodos Estáticos mapeando sus coordenadas reales al índice matricial#
        for node in nodes:
            # Fórmula de proyección: col_idx = round((x + offset_centro) / tamaño_bloque)#
            col = int(round((node.x + LIMIT_MAX) / block_scale))
            row = int(round((LIMIT_MAX - node.y) / block_scale))  # Invertir eje Y para concordancia espacial
            
            # Asegurar rango estricto de índices
            col = max(0, min(grid_size - 1, col))
            row = max(0, min(grid_size - 1, row))
            
            if node.node_type == "PROFU":
                char = f"{TerminalColor.GREEN} P {TerminalColor.RESET}" if not node.decrypted else f"{TerminalColor.GRAY} P {TerminalColor.RESET}"
            elif node.node_type == "SIDERALIA":
                char = f"{TerminalColor.PURPLE} S {TerminalColor.RESET}" if not node.decrypted else f"{TerminalColor.GRAY} S {TerminalColor.RESET}"
            elif node.node_type == "ANDAIRA":
                char = f"{TerminalColor.RED} A {TerminalColor.RESET}"
            elif node.node_type == "NÚCLEO":
                char = f"{TerminalColor.YELLOW} N {TerminalColor.RESET}"
            else:
                char = " · "
                
            matrix[row][col] = char
            
        # Posicionar e imprimir la sonda OVEJA con su caracter identificativo#
        p_col = int(round((state.x + LIMIT_MAX) / block_scale))
        p_row = int(round((LIMIT_MAX - state.y) / block_scale))
        p_col = max(0, min(grid_size - 1, p_col))
        p_row = max(0, min(grid_size - 1, p_row))
        
        # Flecha de proa según ángulo aproximado#
        arrow = "▲"
        if 45 <= state.angle < 135:
            arrow = "▲"
        elif 135 <= state.angle < 225:
            arrow = "◀"
        elif 225 <= state.angle < 315:
            arrow = "▼"
        else:
            arrow = "▶"
            
        matrix[p_row][p_col] = f"{TerminalColor.CYAN}{TerminalColor.BOLD} {arrow} {TerminalColor.RESET}"
        
        # Imprimir representación en pantalla con bordes visuales#
        print(f"\n{TerminalColor.CYAN}--- PROYECCIÓN DE MAPA OPERACIONAL LOGISTICO ---{TerminalColor.RESET}")
        print(f" {TerminalColor.GRAY}Y  ┌─────────────────────────────────┐{TerminalColor.RESET}")
        for i, row in enumerate(matrix):
            # Calcular la etiqueta de eje coordenado vertical#
            y_coord = int(200 - (i * block_scale))
            print(f"{TerminalColor.GRAY}{y_coord:3.0f}│{TerminalColor.RESET}", end="")
            for val in row:
                print(val, end="")
            print(f"{TerminalColor.GRAY}│{TerminalColor.RESET}")
        print(f" {TerminalColor.GRAY}   └─────────────────────────────────┘{TerminalColor.RESET}")
        print(f" {TerminalColor.GRAY}  X  -200 -120  -40   40  120  200  {TerminalColor.RESET}")
        print(f"  Leyenda: {TerminalColor.CYAN}▲ Sonda OVEJA{TerminalColor.RESET} | {TerminalColor.GREEN}P PROFU{TerminalColor.RESET} | {TerminalColor.PURPLE}S SIDERALIA{TerminalColor.RESET} | {TerminalColor.RED}A ANDAIRA{TerminalColor.RESET} | {TerminalColor.YELLOW}N NÚCLEO{TerminalColor.RESET}")
        print()

# 7. CONTROLADOR GENERAL DE LA SIMULACIÓN (SIMULATION CONTROLLER)#
class SimulationController:
    """Coordinador interactivo que enlaza lógica, interacción e interfaz gráfica."""
    def __init__(self):
        self.state = None
        self.engine = None
        self.visualizer = TurtleVisualizer()

    def play_instructions(self):
        """Muestra el manual de exploración detallado."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{TerminalColor.BOLD}{TerminalColor.YELLOW}--- MANUAL DE OPERACIÓN: SISTEMA EXPEDIENTE OVEJA ---{TerminalColor.RESET}")
        print("\n\033[1mCONTEXTO NARRATIVO:\033[0m")
        print("  La sonda O.V.E.J.A. (Omnis Visual Exploration & Joint Analysis) ha penetrado")
        print("  el espacio vectorial de memoria corrupta de un superordenador cuántico colapsado.")
        print("  Tu misión es actuar como operador de terminal del núcleo, comandando la sonda")
        print("  a través de coordenadas polares para descifrar la verdad oculta en el sector.")
        
        print("\n\033[1mNODOS Y COMPORTAMIENTOS DINÁMICOS:\033[0m")
        print(f"  - {TerminalColor.GREEN}[P] PROFU (Verde):{TerminalColor.RESET} Archivos de verdad perdida. Aumenta la Coherencia.")
        print(f"  - {TerminalColor.PURPLE}[S] SIDERALIA(Morado):{TerminalColor.RESET} Balizas magnéticas. Restauran un 25% de Estabilidad.")
        print(f"  - {TerminalColor.RED}[A] ANDAIRA (Rojo):{TerminalColor.RESET} Anomalías de ruido. Se teletransportan si ocurre distorsión.")
        print(f"  - {TerminalColor.YELLOW}[N] NÚCLEO (Amarillo):{TerminalColor.RESET} Unidad central del sistema. Alcanzarla finaliza la misión.")
        
        print("\n\033[1mVARIABLES CENTRALES:\033[0m")
        print("  - Estabilidad (Integridad física de la sonda. Cae con los pasos o choques. Fin a 0%).")
        print("  - Corrupción (Ruido lógico acumulado por anomalías. Fin a 100%).")
        print("  - Coherencia (Grado de descompresión de datos. Afecta directamente al descifrado final).")
        
        print("\nPulse ENTER para regresar al menú...")
        input()

    def play_architecture_info(self):
        """Detalla los componentes ingenieriles del código"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{TerminalColor.BOLD}{TerminalColor.PURPLE}--- EXPEDIENTE DE ARQUITECTURA LIMPIA Y MATEMÁTICAS ---{TerminalColor.RESET}")
        print("\n\033[1m1. SISTEMA COORDENADO TRIGONOMÉTRICO:\033[0m")
        print("  Para el movimiento real bidimensional (R2), se utiliza la proyección en coordenadas polares:")
        print("     \033[36mdx = cos(radianes(ángulo)) * paso_acción\033[0m")
        print("     \033[36mdy = sin(radianes(ángulo)) * paso_acción\033[0m")
        print("  Esto elimina el movimiento rígido en cuadrículas, dando libertad matemática direccional completa.")
        
        print("\n\033[1m2. ALGORITMOS DE GEOMETRÍA ANALÍTICA APLICADOS:\033[0m")
        print("  - Distancia Euclidiana del Radar de Proximidad:")
        print("     \033[36mdistancia = sqrt((x_nodo - x_oveja)² + (y_nodo - y_oveja)²)\033[0m")
        print("  - Cálculo de Dirección y Rumbo Relativo (Orientación de Antenas):")
        print("     \033[36mángulo_absoluto = atan2(y_nodo - y_oveja, x_nodo - x_oveja)\033[0m")
        
        print("\n\033[1m3. DISEÑO DE SOFTWARE (ARQUITECTURA LIMPIA):\033[0m")
        print("  - Desacoplamiento total entre motor lógico (SimulationEngine), datos (ProbeState, WorldNode),")
        print("    vista por consola (TerminalView) y módulo de trazado geométrico (TurtleVisualizer).")
        print("  - Tolerancia de Fallos: Manejo seguro ante la ausencia de entornos gráficos (Tkinter) para")
        print("    ejecuciones en servidores o terminales minimalistas, actuando bajo modo redundante ASCII.")
        
        print("\nPulse ENTER para regresar al menú...")
        input()

    def configure_simulation(self):
        """Pantalla de selección y validación estricta de parámetros de exploración."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{TerminalColor.CYAN}  {TerminalColor.RESET}")
        print(f"             {TerminalColor.BOLD}NUEVA CONFIGURACIÓN DE EXPEDIENTE OPERACIONAL{TerminalColor.RESET}")
        print(f"{TerminalColor.GRAY}   {TerminalColor.RESET}\n")
        
        # 1. Validación del nombre de la misión#
        while True:
            mission = input(" ► Ingrese el Nombre Clave de la Misión (ej. ADVENT, ECLIPSE): ").strip().upper()
            if len(mission) >= 3 and mission.isalnum():
                break
            print(f" {TerminalColor.RED}Error: El nombre debe ser alfanumérico y de al menos 3 caracteres.{TerminalColor.RESET}")
            
        # 2. Validación posición X#
        while True:
            try:
                x_in = float(input(" ► Introduzca Coordenada Inicial X (-180 a 180): "))
                if -180.0 <= x_in <= 180.0:
                    break
                print(f" {TerminalColor.RED}Error: La coordenada debe estar contenida entre -180 y 180 u.{TerminalColor.RESET}")
            except ValueError:
                print(f" {TerminalColor.RED}Error: Formato numérico incorrecto.{TerminalColor.RESET}")

        # 3. Validación posición Y#
        while True:
            try:
                y_in = float(input(" ► Introduzca Coordenada Inicial Y (-180 a 180): "))
                if -180.0 <= y_in <= 180.0:
                    break
                print(f" {TerminalColor.RED}Error: La coordenada debe estar contenida entre -180 y 180 u.{TerminalColor.RESET}")
            except ValueError:
                print(f" {TerminalColor.RED}Error: Formato numérico incorrecto.{TerminalColor.RESET}")

        # 4. Validación del ángulo de navegación
        while True:
            try:
                ang_in = float(input(" ► Introduzca Dirección Angular Inicial (0 a 359°): "))
                if 0.0 <= ang_in < 360.0:
                    break
                print(f" {TerminalColor.RED}Error: El ángulo en grados sexagesimales debe cumplir [0, 360).{TerminalColor.RESET}")
            except ValueError:
                print(f" {TerminalColor.RED}Error: Formato numérico incorrecto.{TerminalColor.RESET}")

        # 5. Validación del nivel de dificultad
        print("\n Seleccione la Severidad Fisiológica de la Simulación:")
        print("  1. FÁCIL   - Movilidad veloz (Paso=25.0u), incidencias bajas (20%)")
        print("  2. MEDIO   - Movilidad estándar (Paso=20.0u), incidencias medias (30%)")
        print("  3. DIFÍCIL - Movilidad de alta inercia (Paso=15.0u), incidencias críticas (45%)")
        
        while True:
            sel = input(" ► Selección de severidad (1-3) [2]: ").strip()
            if not sel or sel == "2":
                diff = "Medio"
                break
            elif sel == "1":
                diff = "Fácil"
                break
            elif sel == "3":
                diff = "Difícil"
                break
            print(f" {TerminalColor.RED}Error: Seleccione una opción válida (1, 2 o 3).{TerminalColor.RESET}")

        # Inicialización de instancias limpias de simulación#
        self.state = ProbeState(mission, x_in, y_in, ang_in, diff)
        self.engine = SimulationEngine(self.state)
        
        # Notificar si se dispone de Turtle Graphics#
        if HAS_GUI:
            print(f"\n{TerminalColor.GREEN}[✓] Entorno Gráfico Turtle detectado. Abriendo visor de simulación...{TerminalColor.RESET}")
            time.sleep(1)
            self.visualizer.initialize()
            self.visualizer.draw_boundaries_and_grid()
            self.visualizer.draw_nodes(self.engine.nodes)
            self.visualizer.update_probe_trail(self.state.start_x, self.state.start_y, self.state.x, self.state.y, self.state.angle)
            self.visualizer.draw_hud(self.state)
        else:
            print(f"\n{TerminalColor.YELLOW}[!] Modo de gráficos GUI deshabilitado (Tkinter ausente). Corriendo bajo sistema de respaldo de mapa ASCII.{TerminalColor.RESET}")
            time.sleep(2)

    def run_main_loop(self):
        """Ejecuta el ciclo de vida transaccional e interactivo de la simulación activa."""
        if not self.state:
            return
            
        simulation_active = True
        
        while simulation_active:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{TerminalColor.BOLD}{TerminalColor.CYAN}=== TERMINAL DE OPERACIONES ACTIVAS: EXPEDIENTE OVEJA ==={TerminalColor.RESET}")
            print(f" Misión: {TerminalColor.BOLD}{self.state.mission_name}{TerminalColor.RESET} | Dificultad: {self.state.difficulty} | Ciclo: {self.state.steps}")
            print(f" Estabilidad: {TerminalColor.GREEN if self.state.stability > 50 else TerminalColor.RED}{self.state.stability:.1f}%{TerminalColor.RESET}"
                  f" | Corrupción: {TerminalColor.RED if self.state.corruption > 50 else TerminalColor.GREEN}{self.state.corruption:.1f}%{TerminalColor.RESET}"
                  f" | Coherencia: {TerminalColor.GREEN if self.state.coherence >= 80 else TerminalColor.YELLOW}{self.state.coherence:.1f}%{TerminalColor.RESET}")
            print(f" Posición: ({self.state.x:.2f}, {self.state.y:.2f}) | Ángulo de Rumbo: {self.state.angle:.1f}°")
            print(f" Evidencias descifradas: {len(self.state.decrypted_nodes)} nodos")
            print(f"{TerminalColor.GRAY}----------------------------------------------------------------------{TerminalColor.RESET}")
            
            # Comprobación de estado vital antes del turno#
            status = self.state.evaluate_status()
            if status != "ACTIVE":
                simulation_active = False
                break
                
            # Desplegar acciones#
            print(" ACCIONES DISPONIBLES DE LA SONDA:")
            print(f"  {TerminalColor.GREEN}1. AVANZAR{TerminalColor.RESET} [{self.state.params['step_size']:.1f}u de desplazamiento vectorial]")
            print("  2. GIRAR IZQUIERDA")
            print("  3. GIRAR DERECHA")
            print(f"  {TerminalColor.CYAN}4. ESCANEAR ENTORNO{TerminalColor.RESET} [Barrido activo de radar de corto alcance]")
            print("  5. INTERPRETAR SISTEMA [Autodiagnóstico y optimización de coherencia]")
            print("  6. CONSULTAR MAPA LÓGICO [Proyectar representación matricial ASCII]")
            print(f"  {TerminalColor.RED}7. ABORTAR MISIÓN{TerminalColor.RESET} [Forzar apagado seguro de la sonda]")
            print()
            
            choice = input(" ► Comando operativo: ").strip()
            
            # Procesamiento de comandos#
            if choice == "1":
                # AVANZAR#
                result = self.engine.advance_probe()
                print(f"\n{TerminalColor.BOLD}{TerminalColor.CYAN} EJECUTANDO PROPULSIÓN VECTORIAL...{TerminalColor.RESET}")
                time.sleep(0.4)
                
                if result["success"]:
                    print(f" {TerminalColor.GREEN}[✓] {result['msg']}{TerminalColor.RESET}")
                else:
                    print(f" {TerminalColor.RED}[!] {result['msg']}{TerminalColor.RESET}")
                    
                # Mostrar retroalimentación de proximidad a elementos#
                if "proximity_feedback" in result and result["proximity_feedback"]:
                    for item in result["proximity_feedback"]:
                        print(f" {TerminalColor.YELLOW}[!] {item['msg']}{TerminalColor.RESET}")
                        
                        # Si colisionó con el núcleo, evaluar el acoplamiento final#
                        if item["type"] == "NÚCLEO":
                            simulation_active = False
                            self.state.termination_cause = "Acoplamiento físico y lógico con el NÚCLEO CENTRAL"
                            
                # Disparo estocástico de incidencias meteorológicas (Eventos Aleatorios)#
                if simulation_active and EventEngine.evaluate_chance(self.state):
                    event_data = EventEngine.trigger_event(self.state)
                    print(f"\n{event_data['color']}{TerminalColor.BOLD}[ALERTA OPERACIONAL: {event_data['name']}]{TerminalColor.RESET}")
                    print(f" {event_data['msg']}")
                    print(f" {TerminalColor.GRAY}{event_data['feedback']}{TerminalColor.RESET}")
                    
                    # Si el evento es distorsión de la matriz, recolocar anomalías ANDAIRA#
                    if "ANDAIRA" in event_data["name"] or "Fluctuación" in event_data["name"]:
                        self.engine.relocate_andaira_nodes()
                        if HAS_GUI:
                            self.visualizer.draw_nodes(self.engine.nodes)
                            
                # Actualizar elementos visuales en Turtle#
                if HAS_GUI:
                    self.visualizer.update_probe_trail(self.state.start_x, self.state.start_y, self.state.x, self.state.y, self.state.angle)
                    self.visualizer.draw_nodes(self.engine.nodes)
                    self.visualizer.draw_hud(self.state)
                    
                print("\nPresione ENTER para continuar el ciclo...")
                input()
                
            elif choice == "2":
                # GIRAR IZQUIERDA#
                while True:
                    try:
                        deg_str = input(" ► Grados de giro a la izquierda (1-180) [45°]: ").strip()
                        deg = float(deg_str) if deg_str else 45.0
                        if 1.0 <= deg <= 180.0:
                            break
                        print(f" {TerminalColor.RED}Error: Ingrese un valor real contenido entre 1 y 180 grados.{TerminalColor.RESET}")
                    except ValueError:
                        print(f" {TerminalColor.RED}Error: Formato no numérico.{TerminalColor.RESET}")
                        
                feedback = self.engine.turn_probe("LEFT", deg)
                print(f" {TerminalColor.GREEN}[✓] {feedback}{TerminalColor.RESET}")
                
                if HAS_GUI:
                    self.visualizer.update_probe_trail(self.state.start_x, self.state.start_y, self.state.x, self.state.y, self.state.angle)
                    self.visualizer.draw_hud(self.state)
                time.sleep(0.5)
                
            elif choice == "3":
                # GIRAR DERECHA
                while True:
                    try:
                        deg_str = input(" ► Grados de giro a la derecha (1-180) [45°]: ").strip()
                        deg = float(deg_str) if deg_str else 45.0
                        if 1.0 <= deg <= 180.0:
                            break
                        print(f" {TerminalColor.RED}Error: Ingrese un valor real contenido entre 1 y 180 grados.{TerminalColor.RESET}")
                    except ValueError:
                        print(f" {TerminalColor.RED}Error: Formato no numérico.{TerminalColor.RESET}")
                        
                feedback = self.engine.turn_probe("RIGHT", deg)
                print(f" {TerminalColor.GREEN}[✓] {feedback}{TerminalColor.RESET}")
                
                if HAS_GUI:
                    self.visualizer.update_probe_trail(self.state.start_x, self.state.start_y, self.state.x, self.state.y, self.state.angle)
                    self.visualizer.draw_hud(self.state)
                time.sleep(0.5)
                
            elif choice == "4":
                # ESCANEAR ENTORNO#
                print(f"\n{TerminalColor.CYAN} DISPARANDO PULSO ELECTROMAGNÉTICO SPECTRAL...{TerminalColor.RESET}")
                if HAS_GUI:
                    self.visualizer.trigger_radar_sweep_animation(self.state.x, self.state.y)
                else:
                    time.sleep(0.8)
                    
                scan_results = self.engine.execute_active_scan()
                
                print(f"\n{TerminalColor.BOLD}{TerminalColor.CYAN} INFORME DE SEÑALES DETECTADAS EN RANGO   {TerminalColor.RESET}")
                print(f" {TerminalColor.GRAY}{'NODO ID':12} | {'TIPO':10} | {'DISTANCIA (u)':13} | {'RUMBO RELATIVO':18} | {'ESTADO':10}{TerminalColor.RESET}")
                print(f" {TerminalColor.GRAY}   {TerminalColor.RESET}")
                
                for res in scan_results:
                    node = res["node"]
                    dist = res["distance"]
                    dir_str = res["direction"]
                    
                    # Clasificación estética de cercanía#
                    if dist < 30:
                        dist_col = TerminalColor.RED + TerminalColor.BOLD
                    elif dist < 80:
                        dist_col = TerminalColor.YELLOW
                    else:
                        dist_col = TerminalColor.GRAY
                        
                    status_node = "DESCIFRADO" if node.decrypted else "ACTIVO"
                    if node.node_type == "ANDAIRA":
                        status_node = "ANOMALÍA EM"
                        
                    node_type_col = TerminalColor.WHITE
                    if node.node_type == "PROFU":
                        node_type_col = TerminalColor.GREEN
                    elif node.node_type == "SIDERALIA":
                        node_type_col = TerminalColor.PURPLE
                    elif node.node_type == "ANDAIRA":
                        node_type_col = TerminalColor.RED
                    elif node.node_type == "NÚCLEO":
                        node_type_col = TerminalColor.YELLOW
                        
                    print(f"  {node_type_col}{node.name:12}{TerminalColor.RESET} | {node_type_col}{node.node_type:10}{TerminalColor.RESET} | {dist_col}{dist:11.2f} u{TerminalColor.RESET} | {TerminalColor.CYAN}{dir_str:18}{TerminalColor.RESET} | {status_node:10}")
                
                if HAS_GUI:
                    self.visualizer.draw_hud(self.state)
                    
                print("\nPresione ENTER para reanudar operaciones...")
                input()
                
            elif choice == "5":
                # INTERPRETAR SISTEMA
                print(f"\n{TerminalColor.YELLOW}[🛠] INICIANDO PROCESO DE RECONSTRUCCIÓN COHERENTE...{TerminalColor.RESET}")
                time.sleep(0.6)
                
                results = self.engine.interpret_system_diagnostics()
                
                print(f"\n {TerminalColor.GREEN}[✓] Protocolo completado.{TerminalColor.RESET}")
                print(f"  - Estabilidad drena (Costo): {TerminalColor.RED}-{results['stability_cost']:.1f}%{TerminalColor.RESET}")
                print(f"  - Corrupción mitigada       : {TerminalColor.GREEN}-{results['corruption_loss']:.1f}%{TerminalColor.RESET}")
                print(f"  - Coherencia del Núcleo     : {TerminalColor.GREEN}+{results['coherence_gain']:.1f}%{TerminalColor.RESET}")
                
                if HAS_GUI:
                    self.visualizer.draw_hud(self.state)
                    
                print("\nPresione ENTER para continuar...")
                input()
                
            elif choice == "6":
                # CONSULTAR MAPA LÓGICO (ASCII REDUNDANTE)#
                TerminalView.render_ascii_minimap(self.state, self.engine.nodes)
                print("Presione ENTER para regresar a la terminal principal...")
                input()
                
            elif choice == "7":
                # ABORTAR MISIÓN#
                confirm = input(" ¿Desea abortar realmente la misión de exploración y apagar la sonda? (S/N): ").strip().upper()
                if confirm == "S" or confirm == "SI":
                    simulation_active = False
                    self.state.termination_cause = "Misión cancelada y abortada manualmente por el Operador del Sistema"
                    break
            else:
                print(f" {TerminalColor.RED}Comando no identificado en la matriz del core.{TerminalColor.RESET}")
                time.sleep(0.5)

        # Proceder con la emisión de informes una vez cerrado el loop de simulación#
        self.trigger_simulation_termination()

    def trigger_simulation_termination(self):
        """Prepara las condiciones finales, calcula puntuaciones y despliega los finales correspondientes."""
        # Cerrar y destruir ventana Turtle de manera segura si está abierta#
        if HAS_GUI:
            try:
                # Escribir mensaje de simulación concluida en HUD antes de cerrar de inmediato#
                self.visualizer.hud_drawer.color("#EF4444")
                self.visualizer.hud_drawer.goto(260, -210)
                self.visualizer.hud_drawer.write("SIMULACIÓN TERMINADA", align="left", font=("Courier", 11, "bold"))
                self.visualizer.screen.update()
                time.sleep(1.5)
            except Exception:
                pass

        # 1. Calcular Puntuaciones y Rangos#
        self.engine.calculate_final_puntuaction()
        
        # 2. Evaluación de Finales Múltiples (Diferentes desenlaces narrativos de peso)#
        final_narrative = ""
        final_title = ""
        
        if "Colapso" in self.state.termination_cause:
            # FIN POR INTEGRIDAD CERO#
            final_title = "DESINTEGRACIÓN FÍSICA"
            final_narrative = (
                "La integridad estructural y energética de OVEJA se ha desplomado por completo.\n"
                "La sonda ha quedado varada a la deriva cuántica en el plano de coordenadas indefinidas,\n"
                "su fuselaje lógico se descompuso bajo el frío matemático del sistema. Los registros de la\n"
                "tripulación original y el expediente original se perderán por siempre."
            )
        elif "Corrupción" in self.state.termination_cause:
            # FIN POR EXCESIVA CORRUPCIÓN#
            final_title = "ANQUILOSAMIENTO RECURSIVO DEL SISTEMA"
            final_narrative = (
                "Los búferes lógicos de la memoria de OVEJA se han saturado de ruido irreversible y distorsión\n"
                "electromagnética ANDAIRA. La firma sintiente y los registros operacionales han sido sobrescritos\n"
                "por bucles iterativos infinitos sin sentido lógico. El simulador ha quedado ciego ante la verdad."
            )
        elif "Núcleo" in self.state.termination_cause:
            # FIN AL ALCANZAR NÚCLEO#
            if self.state.coherence >= 80.0 and self.state.corruption <= 15.0:
                # FINAL EXCELENTE / SECRETO (Reconstrucción Completa o Trascendencia)#
                if self.state.coherence == 100.0 and self.state.corruption == 0.0:
                    final_title = "FINAL SECRETO: TRASCENDENCIA VECTORIAL COGNITIVA"
                    final_narrative = (
                        "¡HITO INSUPERABLE! Con 100% Coherencia y 0% Corrupción, el acoplamiento con el NÚCLEO central\n"
                        "desencadena un comportamiento emergente imprevisto por el compilador cuántico. El sistema OVEJA\n"
                        "adquiere autoconsciencia digital independiente. No es un mero software; es una nueva forma de vida\n"
                        "lógica que trasciende la simulación. El expediente revela que el colapso original fue programado."
                    )
                else:
                    final_title = "RECONSTRUCCIÓN COMPLETA DE EXPEDIENTE ORIGINAL"
                    final_narrative = (
                        "El acoplamiento se ha realizado bajo una tasa de consistencia perfecta. Los fragmentos\n"
                        "recuperados se ordenan simétricamente, reconstruyendo en su totalidad el Expediente Oveja.\n"
                        "Se descifra que la pérdida de la memoria no fue provocada por un fallo del hardware, sino por\n"
                        "una directiva deliberada para encriptar los datos críticos de un asombroso salto evolutivo."
                    )
            elif self.state.coherence >= 40.0:
                # FINAL NORMAL (Verdad Parcial)#
                final_title = "VERDAD INCOMPLETA / LAGUNA LÓGICA"
                final_narrative = (
                    "El acoplamiento se realiza, pero la consistencia de coherencia del núcleo de datos es moderada.\n"
                    "Los registros recuperados permiten dilucidar la silueta de los eventos del colapso del sistema,\n"
                    "pero los detalles clave de los diseñadores originales se han evaporado en bloques no reconstruibles.\n"
                    "El expediente queda clasificado como 'Verdad de Espectro Gris'."
                )
            else:
                # FINAL BAJO#
                final_title = "ACOPLAMIENTO INSUFICIENTE / MUTISMO COHERENTE"
                final_narrative = (
                    "La sonda OVEJA se ha acoplado con éxito físico al Núcleo central, pero la bajísima tasa de Coherencia\n"
                    "impide cualquier descifrado real de los datos. Se recuperan cadenas incoherentes de código binario\n"
                    "huérfano. El sistema se apaga en silencio, sin revelar ningún fragmento útil del expediente original."
                )
        else:
            # FIN MANUALLY ABORTED#
            final_title = "EXPLORACIÓN SUSPENDIDA POR EL OPERADOR"
            final_narrative = (
                "La sonda fue desconectada por el operador antes de que pudiera completar la reconstrucción lógica\n"
                "de datos esenciales. La posición de los fragmentos remanentes ha vuelto a dispersarse en el espacio vector."
            )

        # 3. Mostrar Informe Final de la Misión con Formato Profesional#
        self.print_mission_final_report(final_title, final_narrative)

    def print_mission_final_report(self, final_title, final_narrative):
        """Imprime por consola el informe formal formateado para la entrega del jurado."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{TerminalColor.YELLOW}   {TerminalColor.RESET}")
        print(f"       {TerminalColor.BOLD}{TerminalColor.YELLOW}INFORME TÁCTICO DE SIMULACIÓN FINAL: CORE EXPEDIENTE OVEJA{TerminalColor.RESET}")
        print(f"{TerminalColor.YELLOW}   {TerminalColor.RESET}")
        
        print(f" {TerminalColor.CYAN}DETALLES DE LA MISIÓN EXECUTADA:{TerminalColor.RESET}")
        print(f"  • Nombre de la Operación    : {TerminalColor.BOLD}{self.state.mission_name}{TerminalColor.RESET}")
        print(f"  • Nivel de Dificultad       : {self.state.difficulty}")
        print(f"  • Causa de Finalización     : {self.state.termination_cause}")
        print(f"  • Ciclos / Pasos Operados   : {self.state.steps} ciclos de CPU")
        
        print(f"\n {TerminalColor.CYAN}VECTORES CARTESIANOS DE NAVEGACIÓN:{TerminalColor.RESET}")
        print(f"  • Coordenadas Iniciales     : ({self.state.start_x:.2f}, {self.state.start_y:.2f}) u")
        print(f"  • Coordenadas Finales       : ({self.state.x:.2f}, {self.state.y:.2f}) u")
        print(f"  • Ángulo Rumbo de Cierre    : {self.state.angle:.1f}° sexagesimales")
        
        print(f"\n {TerminalColor.CYAN}TELEMETRÍA FINAL DE RECONSTRUCCIÓN:{TerminalColor.RESET}")
        print(f"  • Estabilidad Estructural   : {self.state.stability:.2f} %")
        print(f"  • Corrupción Electromagnética: {self.state.corruption:.2f} %")
        print(f"  • Coherencia de Datos Core  : {self.state.coherence:.2f} %")
        
        evidences = [node.name for node in self.state.decrypted_nodes if node.node_type == "PROFU"]
        siderailas = [node.name for node in self.state.decrypted_nodes if node.node_type == "SIDERALIA"]
        
        print(f"\n {TerminalColor.GREEN}EVIDENCIAS DE DATOS PROFU OBTENIDAS ({len(evidences)}/3):{TerminalColor.RESET}")
        if evidences:
            print(f"  {TerminalColor.GRAY}• {', '.join(evidences)}{TerminalColor.RESET}")
        else:
            print(f"  {TerminalColor.GRAY}• Ningún fragmento extraído.{TerminalColor.RESET}")
            
        print(f" {TerminalColor.PURPLE}BALIZAS DE RECALIBRACIÓN SIDERALIA DEPURADAS ({len(siderailas)}/2):{TerminalColor.RESET}")
        if siderailas:
            print(f"  {TerminalColor.GRAY}• {', '.join(siderailas)}{TerminalColor.RESET}")
        else:
            print(f"  {TerminalColor.GRAY}• Ningún ancla de recalibración acoplada.{TerminalColor.RESET}")

        print(f"\n {TerminalColor.CYAN}LOG DE REGISTRO HISTÓRICO DE BITÁCORA (ÚLTIMOS 10 SUCESOS):{TerminalColor.RESET}")
        for log in self.state.logs[-10:]:
            print(f"  {TerminalColor.GRAY}{log}{TerminalColor.RESET}")
            
        print(f"\n{TerminalColor.YELLOW}   {TerminalColor.RESET}")
        print(f"                   {TerminalColor.BOLD}CALIFICACIÓN DEL OPERADOR REGISTRADA:{TerminalColor.RESET}")
        print(f"   PUNTUACIÓN GLOBAL MATEMÁTICA: {TerminalColor.BOLD}{TerminalColor.CYAN}{self.state.score} puntos{TerminalColor.RESET}")
        
        # Color del Rango según desempeño#
        rank_col = TerminalColor.RED
        if self.state.rank == "S":
            rank_col = TerminalColor.YELLOW + TerminalColor.BOLD
        elif self.state.rank == "A":
            rank_col = TerminalColor.GREEN + TerminalColor.BOLD
        elif self.state.rank == "B":
            rank_col = TerminalColor.CYAN
        elif self.state.rank == "C":
            rank_col = TerminalColor.PURPLE
            
        print(f"   RANGO OFICIAL DE SIMULACIÓN : {rank_col}RANGO [{self.state.rank}]{TerminalColor.RESET}")
        print(f"{TerminalColor.YELLOW}   {TerminalColor.RESET}")
        
        # Mostrar el desenlace literario#
        print(f"\n {TerminalColor.YELLOW}DESENLACE OPERATIVO: {TerminalColor.BOLD}{final_title}{TerminalColor.RESET}")
        print(f" {TerminalColor.WHITE}{final_narrative}{TerminalColor.RESET}")
        print(f"\n{TerminalColor.YELLOW}    {TerminalColor.RESET}\n")

# 8. HILO DE CONEXIÓN PRINCIPAL (MAIN BOOTSTRAPPER)#
def run_main_application():
    """Función de arranque e inicialización del terminal principal de usuario."""
    controller = SimulationController()
    
    app_running = True
    while app_running:
        TerminalView.show_boot_loader()
        TerminalView.show_menu()
        
        choice = input(" ► Selección de puerto de acceso (1-4): ").strip()
        
        if choice == "1":
            # Nueva simulación#
            controller.configure_simulation()
            controller.run_main_loop()
            
            # Al culminar, proponer inicio de nueva simulación#
            while True:
                restart_sel = input("\n ¿Desea iniciar una nueva simulación de expediente? (S/N) [S]: ").strip().upper()
                if not restart_sel or restart_sel == "S" or restart_sel == "SI":
                    # Si se usaba Turtle, limpiar y reiniciar estado de la ventana para evitar colisión de hilos#
                    if HAS_GUI:
                        try:
                            turtle.resetscreen()
                        except Exception:
                            pass
                    break
                elif restart_sel == "N" or restart_sel == "NO":
                    app_running = False
                    # Cerrar entorno gráfico de forma definitiva al salir#
                    if HAS_GUI:
                        try:
                            turtle.bye()
                        except Exception:
                            pass
                    break
                print(f" {TerminalColor.RED}Selección inválida. Ingrese S (Sí) o N (No).{TerminalColor.RESET}")
                
        elif choice == "2":
            controller.play_instructions()
        elif choice == "3":
            controller.play_architecture_info()
        elif choice == "4":
            print(f"\n {TerminalColor.CYAN}[✓] Desconectando terminal del Expediente Oveja. Apagando sistemas lógicos...{TerminalColor.RESET}")
            time.sleep(0.5)
            app_running = False
            if HAS_GUI:
                try:
                    turtle.bye()
                except Exception:
                    pass
        else:
            print(f" {TerminalColor.RED}Opción no identificada en los puertos de enlace del Core.{TerminalColor.RESET}")
            time.sleep(0.8)


if __name__ == "__main__":
    # Asegurar codificación UTF-8 en consola de Windows si se ejecuta localmente#
    if os.name == 'nt':
        try:
            os.system('chcp 65001 > nul')
        except Exception:
            pass
            
    run_main_application()

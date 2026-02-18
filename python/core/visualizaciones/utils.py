"""
Utilidades para Visualizaciones
================================
Constantes, colores, estilos y funciones de exportación.
Soporta temas light y dark para generación dual de visualizaciones.
"""

import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


# ========== TEMA ACTIVO ==========
# El tema activo controla los colores de fondo, texto y exportación.
# Se cambia dinámicamente con configurar_tema() antes de cada ronda de generación.
_tema_activo = 'light'


# ========== CONFIGURACIÓN DE TAMAÑOS DE FUENTE ==========
# ⚠️ AJUSTE RÁPIDO: Cambia estos valores para ajustar los textos
# Valores recomendados: 1.0 (normal), 1.2 (grande), 1.5 (muy grande), 2.0 (extra grande)

# 👇 CAMBIAR ESTOS DOS VALORES PARA AJUSTAR LOS TAMAÑOS
TITLE_SIZE_MULTIPLIER = 2.0   # 👈 Para TÍTULOS de gráficos
TEXT_SIZE_MULTIPLIER = 1.3    # 👈 Para TEXTO en gráficos (etiquetas, anotaciones, etc.)

# Tamaños base para títulos
_BASE_TITLE_SIZES = {
    'titulo': 16,           # Títulos principales de gráficos
    'titulo_dashboard': 20, # Títulos del dashboard
    'subtitulo': 12,        # Subtítulos
    'subtitulo_dashboard': 11, # Subtítulos del dashboard
}

# Tamaños base para texto de gráficos
_BASE_TEXT_SIZES = {
    'etiquetas': 10,        # Etiquetas de ejes
    'texto': 9,             # Texto en barras, anotaciones
    'texto_pequeno': 8,     # Texto muy pequeño (anotaciones)
    'leyenda': 9,           # Leyendas
    'nota': 9,              # Notas al pie
}

# Tamaños finales calculados (se actualizan automáticamente)
FONT_SIZES = {}
FONT_SIZES.update({k: int(v * TITLE_SIZE_MULTIPLIER) for k, v in _BASE_TITLE_SIZES.items()})
FONT_SIZES.update({k: int(v * TEXT_SIZE_MULTIPLIER) for k, v in _BASE_TEXT_SIZES.items()})


# ========== PALETAS DE COLORES POR TEMA ==========
_COLORES_LIGHT = {
    'positivo': '#4CAF50',      # Verde
    'neutro': '#9E9E9E',        # Gris
    'negativo': '#F44336',      # Rojo
    'primario': '#2196F3',      # Azul
    'secundario': '#FF9800',    # Naranja
    'fondo': '#FFFFFF',         # Blanco
    'texto': '#212121',         # Gris oscuro
    'grid': '#E0E0E0',          # Gris claro
    'borde_separador': 'white', # Para bordes de wedges/bars en pie charts
    'nota': '#757575',          # Gris para notas al pie
}

_COLORES_DARK = {
    'positivo': '#66BB6A',      # Verde (más brillante para fondo oscuro)
    'neutro': '#B0BEC5',        # Gris claro
    'negativo': '#EF5350',      # Rojo (más brillante)
    'primario': '#42A5F5',      # Azul (más brillante)
    'secundario': '#FFA726',    # Naranja (más brillante)
    'fondo': '#0f172a',         # slate-900 - matches app's dark mode background
    'texto': '#E0E0E0',         # Texto claro
    'grid': '#3A3A4A',          # Grid oscuro
    'borde_separador': '#2A2A3A',  # Para bordes de wedges/bars
    'nota': '#9E9E9E',          # Gris para notas al pie
}


# ========== PALETA DE COLORES (mutable, cambia con el tema) ==========
COLORES = dict(_COLORES_LIGHT)

# Paleta por sentimiento
COLORES_SENTIMIENTO = {
    'Positivo': COLORES['positivo'],
    'Neutro': COLORES['neutro'],
    'Negativo': COLORES['negativo']
}

# Paleta para categorías (12 colores únicos)
PALETA_CATEGORIAS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
    '#bcbd22', '#17becf', '#aec7e8', '#ffbb78'
]

# Paleta categorías dark (ligeramente más brillantes)
_PALETA_CATEGORIAS_DARK = [
    '#5B9BD5', '#FFB347', '#77DD77', '#FF6961',
    '#B39DDB', '#A1887F', '#F48FB1', '#B0BEC5',
    '#DCE775', '#4DD0E1', '#90CAF9', '#FFCC80'
]


# ========== ESTILOS (mutable, cambia con el tema) ==========
ESTILOS = {
    'titulo': {
        'fontsize': FONT_SIZES['titulo'],
        'fontweight': 'bold',
        'color': COLORES['texto']
    },
    'subtitulo': {
        'fontsize': FONT_SIZES['subtitulo'],
        'fontweight': 'normal',
        'color': COLORES['texto']
    },
    'etiquetas': {
        'fontsize': FONT_SIZES['etiquetas'],
        'color': COLORES['texto']
    },
    'figura': {
        'facecolor': COLORES['fondo'],
        'dpi': 300
    }
}


# ========== CONFIGURACIÓN DE EXPORTACIÓN (mutable, cambia con el tema) ==========
CONFIG_EXPORT = {
    'format': 'png',
    'dpi': 300,
    'bbox_inches': 'tight',
    'facecolor': 'white',
    'edgecolor': 'none',
    'transparent': False
}


# ========== FUNCIONES DE UTILIDAD ==========

def get_tema_activo() -> str:
    """Retorna el tema activo actual ('light' o 'dark')."""
    return _tema_activo


def configurar_tema(tema: str = 'light'):
    """
    Configura el tema de colores para la generación de visualizaciones.
    
    Actualiza in-place los diccionarios globales COLORES, COLORES_SENTIMIENTO,
    ESTILOS, CONFIG_EXPORT y PALETA_CATEGORIAS para que todos los generadores
    que los importan por referencia vean los nuevos valores automáticamente.
    
    Args:
        tema: 'light' o 'dark'
    """
    global _tema_activo
    _tema_activo = tema
    
    fuente = _COLORES_DARK if tema == 'dark' else _COLORES_LIGHT
    
    # Actualizar COLORES in-place
    COLORES.clear()
    COLORES.update(fuente)
    
    # Actualizar COLORES_SENTIMIENTO in-place
    COLORES_SENTIMIENTO['Positivo'] = COLORES['positivo']
    COLORES_SENTIMIENTO['Neutro'] = COLORES['neutro']
    COLORES_SENTIMIENTO['Negativo'] = COLORES['negativo']
    
    # Actualizar PALETA_CATEGORIAS in-place
    nueva_paleta = _PALETA_CATEGORIAS_DARK if tema == 'dark' else [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
        '#bcbd22', '#17becf', '#aec7e8', '#ffbb78'
    ]
    PALETA_CATEGORIAS.clear()
    PALETA_CATEGORIAS.extend(nueva_paleta)
    
    # Actualizar ESTILOS in-place
    ESTILOS['titulo']['color'] = COLORES['texto']
    ESTILOS['subtitulo']['color'] = COLORES['texto']
    ESTILOS['etiquetas']['color'] = COLORES['texto']
    ESTILOS['figura']['facecolor'] = COLORES['fondo']
    
    # Actualizar CONFIG_EXPORT in-place
    CONFIG_EXPORT['facecolor'] = COLORES['fondo']


def guardar_figura(fig, ruta: Path, cerrar: bool = True):
    """
    Guarda una figura de matplotlib/seaborn en PNG.
    
    Args:
        fig: Figura de matplotlib
        ruta: Path donde guardar
        cerrar: Si True, cierra la figura después de guardar
    """
    # Crear directorio si no existe
    ruta.parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar
    fig.savefig(ruta, **CONFIG_EXPORT)
    
    # Cerrar para liberar memoria
    if cerrar:
        plt.close(fig)


def configurar_estilo_grafico():
    """Configura el estilo global de matplotlib/seaborn según el tema activo."""
    if _tema_activo == 'dark':
        plt.style.use('dark_background')
    else:
        plt.style.use('seaborn-v0_8-darkgrid')
    
    plt.rcParams['figure.facecolor'] = COLORES['fondo']
    plt.rcParams['axes.facecolor'] = COLORES['fondo']
    plt.rcParams['text.color'] = COLORES['texto']
    plt.rcParams['axes.labelcolor'] = COLORES['texto']
    plt.rcParams['xtick.color'] = COLORES['texto']
    plt.rcParams['ytick.color'] = COLORES['texto']
    plt.rcParams['axes.edgecolor'] = COLORES['grid']
    plt.rcParams['grid.color'] = COLORES['grid']
    plt.rcParams['legend.facecolor'] = COLORES['fondo']
    plt.rcParams['legend.edgecolor'] = COLORES['grid']
    plt.rcParams['font.size'] = FONT_SIZES['etiquetas']
    plt.rcParams['figure.dpi'] = 100


def truncar_texto(texto: str, max_len: int = 30) -> str:
    """Trunca texto para etiquetas."""
    if len(texto) <= max_len:
        return texto
    return texto[:max_len-3] + '...'

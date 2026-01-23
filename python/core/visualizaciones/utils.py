"""
Utilidades para Visualizaciones
================================
Constantes, colores, estilos y funciones de exportación.
"""

import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


# ========== PALETA DE COLORES ==========
COLORES = {
    'positivo': '#4CAF50',      # Verde
    'neutro': '#9E9E9E',        # Gris
    'negativo': '#F44336',      # Rojo
    'primario': '#2196F3',      # Azul
    'secundario': '#FF9800',    # Naranja
    'fondo': '#FFFFFF',         # Blanco
    'texto': '#212121',         # Gris oscuro
    'grid': '#E0E0E0',          # Gris claro
}

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


# ========== ESTILOS ==========
ESTILOS = {
    'titulo': {
        'fontsize': 16,
        'fontweight': 'bold',
        'color': COLORES['texto']
    },
    'subtitulo': {
        'fontsize': 12,
        'fontweight': 'normal',
        'color': COLORES['texto']
    },
    'etiquetas': {
        'fontsize': 10,
        'color': COLORES['texto']
    },
    'figura': {
        'facecolor': COLORES['fondo'],
        'dpi': 300
    }
}


# ========== CONFIGURACIÓN DE EXPORTACIÓN ==========
CONFIG_EXPORT = {
    'format': 'png',
    'dpi': 300,
    'bbox_inches': 'tight',
    'facecolor': 'white',
    'edgecolor': 'none',
    'transparent': False
}


# ========== FUNCIONES DE UTILIDAD ==========

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
    """Configura el estilo global de matplotlib/seaborn."""
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.facecolor'] = COLORES['fondo']
    plt.rcParams['axes.facecolor'] = COLORES['fondo']
    plt.rcParams['text.color'] = COLORES['texto']
    plt.rcParams['axes.labelcolor'] = COLORES['texto']
    plt.rcParams['xtick.color'] = COLORES['texto']
    plt.rcParams['ytick.color'] = COLORES['texto']
    plt.rcParams['font.size'] = 10
    plt.rcParams['figure.dpi'] = 100


def truncar_texto(texto: str, max_len: int = 30) -> str:
    """Trunca texto para etiquetas."""
    if len(texto) <= max_len:
        return texto
    return texto[:max_len-3] + '...'

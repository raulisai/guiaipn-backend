"""
Generador de comandos para el canvas
"""
from typing import List


def generate_rectangle(x: int, y: int, width: int, height: int, color: str = "#3498db") -> dict:
    """
    Genera comando para dibujar un rectángulo
    
    Args:
        x, y: Posición
        width, height: Dimensiones
        color: Color en formato hex
        
    Returns:
        dict: Comando de canvas
    """
    return {
        "type": "rectangle",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "color": color
    }


def generate_circle(x: int, y: int, radius: int, color: str = "#e74c3c") -> dict:
    """
    Genera comando para dibujar un círculo
    
    Args:
        x, y: Centro
        radius: Radio
        color: Color en formato hex
        
    Returns:
        dict: Comando de canvas
    """
    return {
        "type": "circle",
        "x": x,
        "y": y,
        "radius": radius,
        "color": color
    }


def generate_line(x1: int, y1: int, x2: int, y2: int, color: str = "#2c3e50", width: int = 2) -> dict:
    """
    Genera comando para dibujar una línea
    
    Args:
        x1, y1: Punto inicial
        x2, y2: Punto final
        color: Color en formato hex
        width: Grosor de la línea
        
    Returns:
        dict: Comando de canvas
    """
    return {
        "type": "line",
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "color": color,
        "width": width
    }


def generate_text(x: int, y: int, text: str, size: int = 16, color: str = "#000000") -> dict:
    """
    Genera comando para dibujar texto
    
    Args:
        x, y: Posición
        text: Texto a mostrar
        size: Tamaño de fuente
        color: Color en formato hex
        
    Returns:
        dict: Comando de canvas
    """
    return {
        "type": "text",
        "x": x,
        "y": y,
        "text": text,
        "size": size,
        "color": color
    }


def generate_axis(x: int, y: int, width: int, height: int) -> dict:
    """
    Genera comando para dibujar ejes cartesianos
    
    Args:
        x, y: Origen
        width, height: Dimensiones
        
    Returns:
        dict: Comando de canvas
    """
    return {
        "type": "axis",
        "x": x,
        "y": y,
        "width": width,
        "height": height
    }

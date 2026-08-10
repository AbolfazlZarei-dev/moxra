# -*- coding: utf-8 -*-
"""
Moxra - Professional NSFW Content Detection Library

A lightweight, high-performance NSFW content detection library
for images, GIFs, and videos using ONNX Runtime.

Example:
    >>> from moxra import MoxraDetector
    >>> detector = MoxraDetector()
    >>> result = detector.predict_image("image.jpg")
    >>> print(result)
    {'neutral': 0.85, 'sexy': 0.08, 'porn': 0.04, 'hentai': 0.02, 'drawing': 0.01}
"""

from .core.detector import MoxraDetector
from .core.config import Config, CATEGORIES
from .api.app import create_app, run_server

__version__ = "1.0.0"
__author__ = "Moxra Team"
__all__ = [
    'MoxraDetector',
    'Config',
    'CATEGORIES',
    'create_app',
    'run_server'
]
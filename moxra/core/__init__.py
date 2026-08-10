# -*- coding: utf-8 -*-
"""Core module - detection engine, models, configuration"""

from .detector import MoxraDetector
from .config import Config, CATEGORIES, MODEL_TYPES
from .models import ModelManager

__all__ = [
    'MoxraDetector',
    'Config',
    'CATEGORIES',
    'MODEL_TYPES',
    'ModelManager'
]
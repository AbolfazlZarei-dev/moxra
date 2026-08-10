# -*- coding: utf-8 -*-
"""
Moxra - Processors Module

This module provides specialized processors for different media types:
- ImageProcessor: Handles single images (JPG, PNG, WEBP, BMP)
- GIFProcessor: Handles animated GIFs with frame extraction
- VideoProcessor: Handles video files (MP4, AVI, MOV, MKV, etc.)
"""

from .image import ImageProcessor
from .gif import GIFProcessor
from .video import VideoProcessor

__all__ = ['ImageProcessor', 'GIFProcessor', 'VideoProcessor']
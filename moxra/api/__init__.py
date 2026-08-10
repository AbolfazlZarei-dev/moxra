# -*- coding: utf-8 -*-
"""
Moxra - API Module

This module provides the FastAPI application and routes for the Moxra API.
It includes all request/response models and exposes the public API endpoints.

Features:
    - Public API endpoints without authentication
    - Image, GIF, and video classification
    - URL-based classification
    - Health check endpoint
    - Memory cleanup endpoint
"""

from .app import create_app, run_server
from .routes import router
from .models import (
    ClassifyRequest,
    ClassifyResponse,
    ClassifyURLRequest,
    HealthResponse,
    ErrorResponse
)

__all__ = [
    'create_app',
    'run_server',
    'router',
    'ClassifyRequest',
    'ClassifyResponse',
    'ClassifyURLRequest',
    'HealthResponse',
    'ErrorResponse'
]
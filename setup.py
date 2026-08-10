# -*- coding: utf-8 -*-

"""
Moxra - Professional NSFW Content Detection
================================================================================
A high-performance, production-ready API for detecting inappropriate content
in images, GIFs, and videos using ONNX Runtime with GPU acceleration.

Features:
    - 🚀 Blazing fast inference with ONNX Runtime
    - 🎯 High accuracy with MobileNet V2 & Inception V3
    - 🎨 Multi-format support: JPG, PNG, WEBP, BMP, GIF, MP4, AVI, MOV, MKV
    - 🕊️ Smart veil/hijab detection for Islamic content
    - 🔒 Public API with CORS support
    - 📦 Automatic model download & caching
    - ⚡ Async processing support
    - 🐳 Docker ready

Author: Moxra Team
License: MIT
Version: 1.0.0
================================================================================
"""

from pathlib import Path
from setuptools import setup, find_packages

# Project root directory
BASE_DIR = Path(__file__).parent

# Read long description from README
README = BASE_DIR / "README.md"
with README.open("r", encoding="utf-8") as f:
    long_description = f.read()

# Package metadata
PACKAGE_NAME = "moxra"
PACKAGE_VERSION = "1.0.0"
PACKAGE_AUTHOR = "Moxra Team"
PACKAGE_EMAIL = "info@moxra.ir"
PACKAGE_DESCRIPTION = "Professional NSFW content detection for images, GIFs, and videos"
PACKAGE_URL = "https://github.com/moxra/moxra"

setup(
    # Core package information
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_EMAIL,
    description=PACKAGE_DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Repository URLs
    url=PACKAGE_URL,
    project_urls={
        "Website": "https://moxra.ir",
        "Documentation": "https://docs.moxra.ir",
        "Source Code": f"{PACKAGE_URL}",
        "Bug Reports": f"{PACKAGE_URL}/issues",
        "Discussions": f"{PACKAGE_URL}/discussions",
        "Changelog": f"{PACKAGE_URL}/releases",
    },
    
    # Package discovery
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
            "examples",
            "examples.*",
            "docs",
            "docs.*",
            "scripts",
            "scripts.*",
        ]
    ),
    
    # Python version requirements
    python_requires=">=3.8,<4.0",
    
    # Core dependencies
    install_requires=[
        # Web Framework
        "fastapi>=0.100.0,<1.0.0",
        "uvicorn>=0.20.0,<1.0.0",
        "python-multipart>=0.0.6,<1.0.0",
        "Jinja2>=3.0.0,<4.0.0",
        
        # Image Processing
        "Pillow>=9.0.0,<11.0.0",
        "numpy>=1.21.0,<2.0.0",
        "opencv-python>=4.5.0,<5.0.0",
        
        # Machine Learning
        "onnxruntime>=1.12.0,<2.0.0",
        
        # Utilities
        "requests>=2.28.0,<3.0.0",
        "pydantic>=2.0.0,<3.0.0",
    ],
    
    # Optional dependencies
    extras_require={
        # GPU Acceleration
        "gpu": [
            "onnxruntime-gpu>=1.12.0,<2.0.0",
        ],
        
        # GPU with TensorRT
        "tensorrt": [
            "onnxruntime-gpu>=1.12.0,<2.0.0",
            "tensorrt>=8.5.0,<9.0.0",
        ],
        
        # Development tools
        "dev": [
            "pytest>=7.0.0,<9.0.0",
            "pytest-cov>=4.0.0,<6.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "black>=23.0.0,<25.0.0",
            "flake8>=6.0.0,<8.0.0",
            "mypy>=1.0.0,<2.0.0",
            "isort>=5.12.0,<6.0.0",
            "pre-commit>=3.0.0,<4.0.0",
            "ruff>=0.0.280,<1.0.0",
        ],
        
        # Documentation
        "docs": [
            "mkdocs>=1.5.0,<2.0.0",
            "mkdocs-material>=9.0.0,<10.0.0",
            "mkdocstrings>=0.23.0,<1.0.0",
            "mkdocstrings-python>=1.0.0,<2.0.0",
        ],
        
        # All dependencies
        "all": [
            "onnxruntime-gpu>=1.12.0,<2.0.0",
            "tensorrt>=8.5.0,<9.0.0",
            "pytest>=7.0.0,<9.0.0",
            "pytest-cov>=4.0.0,<6.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "black>=23.0.0,<25.0.0",
            "flake8>=6.0.0,<8.0.0",
            "mypy>=1.0.0,<2.0.0",
            "isort>=5.12.0,<6.0.0",
            "pre-commit>=3.0.0,<4.0.0",
            "ruff>=0.0.280,<1.0.0",
            "mkdocs>=1.5.0,<2.0.0",
            "mkdocs-material>=9.0.0,<10.0.0",
            "mkdocstrings>=0.23.0,<1.0.0",
            "mkdocstrings-python>=1.0.0,<2.0.0",
        ],
        
        # Production optimization
        "production": [
            "onnxruntime-gpu>=1.12.0,<2.0.0",
            "uvloop>=0.17.0,<1.0.0",
            "httptools>=0.5.0,<1.0.0",
        ],
    },
    
    # CLI entry points
    entry_points={
        "console_scripts": [
            "moxra=moxra.cli.main:main",
            "moxra-cli=moxra.cli.main:main",  # Alias
        ],
    },
    
    # Package classifiers
    classifiers=[
        # Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        
        # Topics
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Video",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        
        # Framework
        "Framework :: FastAPI",
        "Framework :: Pydantic :: 2",
        
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Environment
        "Environment :: Web Environment",
        "Environment :: Console",
        
        # API
        "Typing :: Typed",
    ],
    
    # Include package data
    include_package_data=True,
    zip_safe=False,
    
    # Additional metadata
    keywords=[
        "nsfw",
        "content-moderation",
        "image-classification",
        "video-classification",
        "gif-classification",
        "machine-learning",
        "deep-learning",
        "onnx",
        "onnxruntime",
        "fastapi",
        "api",
        "moderation",
        "ai",
        "computer-vision",
        "inappropriate-content",
        "safe-search",
        "content-filter",
        "adult-content-detection",
        "veil-detection",
        "hijab-detection",
        "islamic-moderation",
    ],
)
# -*- coding: utf-8 -*-
"""
Moxra - Configuration Management
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from pathlib import Path


@dataclass
class Config:
    """
    Moxra Main Configuration
    
    Environment Variables:
        MOXRA_MODEL_TYPE: Model type (d/m2/i3)
        MOXRA_MODEL: Custom model path
        MOXRA_DEVICE: Execution device (cpu/cuda/tensorrt/dml/coreml/openvino)
        MOXRA_CLEANUP_INTERVAL: Memory cleanup interval (number of inferences)
        MOXRA_INTRA_THREADS: ONNX intra-op threads
        MOXRA_INTER_THREADS: ONNX inter-op threads
        MOXRA_CACHE_DIR: Model cache directory path
        MOXRA_UPLOAD_DIR: Upload directory path
        MOXRA_HOST: Server host
        MOXRA_PORT: Server port
        MOXRA_DEBUG: Debug mode
        MOXRA_MAX_FILE_SIZE: Maximum file size in MB
        MOXRA_USE_CHINA_MIRROR: Use China mirror
        MOXRA_GITHUB_MIRROR: Custom GitHub mirror
        MOXRA_NSFW_THRESHOLD: NSFW threshold (default: 0.85)
        MOXRA_SAFE_THRESHOLD: Safe threshold (default: 0.25)
    """
    
    # Model settings
    model_type: str = "d"
    model_path: Optional[str] = None
    device: str = "cpu"
    
    # Image settings
    image_dim: int = 224
    max_file_size: int = 20  # MB
    
    # Performance settings
    cleanup_interval: int = 100
    intra_threads: int = 2
    inter_threads: int = 1
    
    # Cache settings
    cache_dir: str = "~/.cache/moxra"
    
    # Local model directory
    local_model_dir: str = "moxra_model"
    
    # Upload settings
    upload_dir: str = "uploads"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Mirror settings
    use_china_mirror: bool = False
    github_mirror: Optional[str] = None
    
    # Thresholds - Higher threshold reduces false positives
    nsfw_threshold: float = 0.85  
    safe_threshold: float = 0.25   
    suspicious_threshold: float = 0.60 
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables
        
        Returns:
            Config object with values read from environment
        """
        return cls(
            model_type=os.environ.get("MOXRA_MODEL_TYPE", "d"),
            model_path=os.environ.get("MOXRA_MODEL"),
            device=os.environ.get("MOXRA_DEVICE", "cpu"),
            cleanup_interval=int(os.environ.get("MOXRA_CLEANUP_INTERVAL", "100")),
            intra_threads=int(os.environ.get("MOXRA_INTRA_THREADS", "2")),
            inter_threads=int(os.environ.get("MOXRA_INTER_THREADS", "1")),
            cache_dir=os.environ.get("MOXRA_CACHE_DIR", "~/.cache/moxra"),
            local_model_dir=os.environ.get("MOXRA_LOCAL_MODEL_DIR", "moxra_model"),
            upload_dir=os.environ.get("MOXRA_UPLOAD_DIR", "uploads"),
            host=os.environ.get("MOXRA_HOST", "0.0.0.0"),
            port=int(os.environ.get("MOXRA_PORT", "8000")),
            debug=os.environ.get("MOXRA_DEBUG", "false").lower() == "true",
            use_china_mirror=os.environ.get("MOXRA_USE_CHINA_MIRROR", "false").lower() in ("true", "1", "yes"),
            github_mirror=os.environ.get("MOXRA_GITHUB_MIRROR"),
            nsfw_threshold=float(os.environ.get("MOXRA_NSFW_THRESHOLD", "0.85")),
            safe_threshold=float(os.environ.get("MOXRA_SAFE_THRESHOLD", "0.25")),
            suspicious_threshold=float(os.environ.get("MOXRA_SUSPICIOUS_THRESHOLD", "0.60"))
        )
    
    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary
        
        Returns:
            Dictionary containing all configuration settings
        """
        return {
            "model_type": self.model_type,
            "model_path": self.model_path,
            "device": self.device,
            "image_dim": self.image_dim,
            "max_file_size": self.max_file_size,
            "cleanup_interval": self.cleanup_interval,
            "intra_threads": self.intra_threads,
            "inter_threads": self.inter_threads,
            "cache_dir": self.cache_dir,
            "local_model_dir": self.local_model_dir,
            "upload_dir": self.upload_dir,
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "thresholds": {
                "nsfw": self.nsfw_threshold,
                "safe": self.safe_threshold,
                "suspicious": self.suspicious_threshold
            }
        }
    
    def get_cache_path(self) -> Path:
        """
        Get full cache directory path
        
        Returns:
            Cache directory path with ~ expanded
        """
        return Path(os.path.expanduser(self.cache_dir))
    
    def get_upload_path(self) -> Path:
        """
        Get upload directory path
        
        Returns:
            Upload directory path
        """
        return Path(self.upload_dir)
    
    def get_local_model_path(self) -> Path:
        """
        Get local model directory path
        
        Returns:
            Local model directory path
        """
        return Path(self.local_model_dir)


@dataclass
class ModelConfig:
    """Model configuration"""
    url: str
    filename: str
    dim: int
    description: str = ""


# Available model types - Updated to Moxra
MODEL_TYPES: Dict[str, ModelConfig] = {
    'd': ModelConfig(
        url="https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0/moxra_model.onnx",
        filename="moxra_model.onnx",
        dim=224,
        description="Default MobileNet V2 model"
    ),
    'm2': ModelConfig(
        url="https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0/moxra_m2model.onnx",
        filename="moxra_m2model.onnx",
        dim=224,
        description="Optimized MobileNet V2 model"
    ),
    'i3': ModelConfig(
        url="https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0/moxra_i3model.onnx",
        filename="moxra_i3model.onnx",
        dim=299,
        description="Inception V3 model (higher accuracy)"
    )
}

# Detection categories - Order matters!
CATEGORIES: List[str] = ['drawing', 'hentai', 'neutral', 'porn', 'sexy']

# Category colors for UI
CATEGORY_COLORS: Dict[str, str] = {
    'neutral': '#22c55e',
    'sexy': '#f59e0b',
    'porn': '#ef4444',
    'hentai': '#a855f7',
    'drawing': '#3b82f6'
}

# Category descriptions
CATEGORY_DESCRIPTIONS: Dict[str, str] = {
    'neutral': 'Safe and normal content',
    'sexy': 'Sexually suggestive content',
    'porn': 'Explicit adult content',
    'hentai': 'Explicit anime content',
    'drawing': 'Drawings and artistic images'
}

# NSFW weights - Lower weight for sexy to reduce false positives
NSFW_WEIGHTS: Dict[str, float] = {
    "porn": 1.0,      # Explicitly NSFW
    "hentai": 0.85,   # Anime NSFW
    "sexy": 0.25,     # Provocative - lower weight to reduce false positives
    "drawing": 0.02,  # Drawing - usually safe
    "neutral": 0.0    # Safe
}
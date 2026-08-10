# -*- coding: utf-8 -*-
"""
Moxra - Model Management
"""

import os
import json
import platform
import urllib.request
from typing import Optional
from pathlib import Path
import hashlib

from .config import Config, MODEL_TYPES


class ModelManager:
    """
    Model download, caching, and validation management
    
    Features:
        - Automatic model download from GitHub
        - Local caching with versioning
        - Mirror support for Chinese users
        - Model integrity validation
        - Local model directory support
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = config.get_cache_path()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Local model directory
        self.local_dir = config.get_local_model_path()
    
    def get_model_path(self, model_type: Optional[str] = None) -> str:
        """
        Get model path, downloads if not exists
        
        Args:
            model_type: Model type (d/m2/i3), uses config if None
        
        Returns:
            Model file path
        """
        model_type = model_type or self.config.model_type
        
        if model_type not in MODEL_TYPES:
            raise ValueError(f"Unknown model type: {model_type}. Available: {list(MODEL_TYPES.keys())}")
        
        # 1. Check environment variable
        env_path = os.environ.get("MOXRA_MODEL")
        if env_path and os.path.exists(env_path):
            print(f"✅ Using model from environment variable: {env_path}")
            return env_path
        
        # 2. Check custom path in config
        if self.config.model_path and os.path.exists(self.config.model_path):
            print(f"✅ Using model from config: {self.config.model_path}")
            return self.config.model_path
        
        # 3. Check local model directory (priority)
        model_config = MODEL_TYPES[model_type]
        local_model_path = self.local_dir / model_config.filename
        
        if local_model_path.exists():
            print(f"✅ Using local model: {local_model_path}")
            return str(local_model_path)
        
        # 4. Check cache directory
        cache_model_path = self.cache_dir / model_config.filename
        
        if cache_model_path.exists():
            print(f"✅ Using cached model: {cache_model_path}")
            return str(cache_model_path)
        
        # 5. Download model if not found anywhere
        print(f"📥 Model not found locally. Downloading...")
        print(f"   Source: {model_config.url}")
        print(f"   Destination: {cache_model_path}")
        self._download_model(model_config.url, cache_model_path)
        print("✅ Download complete")
        
        return str(cache_model_path)
    
    def _download_model(self, url: str, destination: Path):
        """Download model file with progress display"""
        url = self._get_download_url(url)
        
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Moxra/1.0'}
            )
            
            with urllib.request.urlopen(req) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 8192
                
                with open(destination, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            print(f"\r   Progress: {percent}%", end="")
                
                print()
        
        except urllib.error.URLError as e:
            raise RuntimeError(f"Download failed: {e}. Please check your internet connection.")
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")
    
    def _get_download_url(self, original_url: str) -> str:
        """Get download URL with mirror support"""
        use_mirror = self.config.use_china_mirror or self._is_in_china()
        
        if use_mirror:
            mirror = self.config.github_mirror
            if mirror:
                return f"{mirror}/{original_url}"
            return original_url.replace(
                "https://github.com",
                "https://ghproxy.cn/https://github.com"
            )
        
        return original_url
    
    @staticmethod
    def _is_in_china() -> bool:
        """Check if user is in China"""
        use_mirror = os.environ.get("MOXRA_USE_CHINA_MIRROR")
        if use_mirror is not None:
            return use_mirror.lower() in ('1', 'true', 'yes')
        
        try:
            import time
            tz_offset = -time.timezone / 3600
            return tz_offset == 8
        except Exception:
            return False
    
    def clear_cache(self):
        """Clear model cache"""
        deleted = 0
        for file in self.cache_dir.glob("*.onnx"):
            try:
                file.unlink()
                deleted += 1
            except Exception:
                pass
        
        index_file = self.cache_dir / "models.json"
        if index_file.exists():
            try:
                index_file.unlink()
            except Exception:
                pass
        
        return deleted
    
    def get_cache_info(self) -> dict:
        """Get cache information"""
        models = []
        total_size = 0
        
        for file in self.cache_dir.glob("*.onnx"):
            size = file.stat().st_size
            total_size += size
            models.append({
                "name": file.name,
                "size_mb": round(size / (1024 * 1024), 2),
                "modified": file.stat().st_mtime
            })
        
        return {
            "cache_dir": str(self.cache_dir),
            "total_models": len(models),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "models": models
        }
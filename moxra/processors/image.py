# -*- coding: utf-8 -*-
"""
Moxra - Image Processor
"""

import os
import io
from typing import Optional, Union, Tuple
from PIL import Image
import numpy as np

from ..core.config import Config


class ImageProcessor:
    """
    Single image processor for NSFW content detection
    
    Supports: JPG, PNG, WEBP, BMP, TIFF, GIF (first frame only)
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.image_dim = config.image_dim
        self.max_file_size = config.max_file_size * 1024 * 1024
    
    def process(self, image_path: str) -> Optional[np.ndarray]:
        """
        Process image from file path
        
        Args:
            image_path: Path to image file
        
        Returns:
            Preprocessed image as numpy array (N, H, W, C)
        """
        try:
            # Check file size
            if os.path.getsize(image_path) > self.max_file_size:
                print(f"⚠️ File size is too large: {os.path.getsize(image_path)} bytes, but continuing processing")
            
            image = Image.open(image_path)
            
            # If GIF, take first frame
            if image.format == 'GIF':
                try:
                    image.seek(0)
                except:
                    pass
            
            return self._process_image(image)
        
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Process image from binary data
        
        Args:
            image_bytes: Image data as bytes
        
        Returns:
            Preprocessed image as numpy array
        """
        try:
            if len(image_bytes) > self.max_file_size:
                print(f"⚠️ Data size is too large: {len(image_bytes)} bytes, but continuing processing")
            
            image = Image.open(io.BytesIO(image_bytes))
            
            # If GIF, take first frame
            if image.format == 'GIF':
                try:
                    image.seek(0)
                except:
                    pass
            
            return self._process_image(image)
        
        except Exception as e:
            print(f"Error processing binary data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _process_image(self, image: Image.Image) -> np.ndarray:
        """
        Internal image processing
        
        Args:
            image: PIL Image object
        
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Convert to RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize
            resized = image.resize((self.image_dim, self.image_dim), Image.BICUBIC)
            
            # Convert to numpy array and normalize
            img_array = np.array(resized, dtype=np.float32) / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        
        except Exception as e:
            print(f"Error in internal image processing: {e}")
            raise
# -*- coding: utf-8 -*-
"""
Moxra - GIF Processor
"""

import os
import gc
from typing import Optional, Dict, Callable, List
from PIL import Image
import numpy as np

from ..core.config import Config


class GIFProcessor:
    """
    GIF animation processor for NSFW content detection
    
    Has multiple fallback methods to support corrupted or unusual GIF files
    """
    
    def __init__(self, config: Config, predict_fn: Callable):
        self.config = config
        self.image_dim = config.image_dim
        self.predict_fn = predict_fn
        self.max_frames = 100
    
    def process(self, gif_path: str) -> Optional[Dict[str, float]]:
        """
        Process GIF file with multiple fallback methods
        
        Args:
            gif_path: Path to GIF file
        
        Returns:
            Average predictions from all frames
        """
        try:
            # Check file size
            file_size = os.path.getsize(gif_path)
            if file_size > self.config.max_file_size * 1024 * 1024:
                print(f"⚠️ GIF file size is too large: {file_size} bytes")
            
            # Method 1: Try PIL
            result = self._try_pil_method(gif_path)
            if result is not None:
                return result
            
            # Method 2: Try OpenCV
            result = self._try_opencv_method(gif_path)
            if result is not None:
                return result
            
            # Method 3: Try imageio
            result = self._try_imageio_method(gif_path)
            if result is not None:
                return result
            
            # Method 4: Try reading as bytes
            result = self._try_bytes_method(gif_path)
            if result is not None:
                return result
            
            print(f"❌ All GIF processing methods failed for: {gif_path}")
            return None
        
        except Exception as e:
            print(f"❌ Error processing GIF {gif_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _try_pil_method(self, gif_path: str) -> Optional[Dict[str, float]]:
        """Method 1: PIL with error handling"""
        try:
            # Check file header
            with open(gif_path, 'rb') as f:
                header = f.read(6)
            
            # Check GIF header
            if not (header[:3] == b'GIF' or header[:4] == b'\x00\x00\x00\x00'):
                print(f"⚠️ Invalid GIF file (header: {header[:6]})")
                return None
            
            # Try to open with PIL
            image = Image.open(gif_path)
            
            # Check if it's animated
            is_animated = False
            try:
                is_animated = getattr(image, 'is_animated', False) or \
                             (image.format == 'GIF' and getattr(image, 'n_frames', 1) > 1)
            except:
                pass
            
            if not is_animated:
                # Process as single image
                print("ℹ️ GIF is not animated, processing as single frame")
                image.seek(0)
                frame = image.convert('RGB')
                resized = frame.resize((self.image_dim, self.image_dim), Image.BICUBIC)
                img_array = np.array(resized, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                predictions = self.predict_fn(img_array)
                return self._format_predictions(predictions)
            
            # Process animation
            return self._process_animated_pil(image)
            
        except Exception as e:
            print(f"⚠️ PIL method failed: {e}")
            return None
    
    def _process_animated_pil(self, gif: Image.Image) -> Optional[Dict[str, float]]:
        """Process animated GIF using PIL"""
        try:
            frame_count = min(gif.n_frames, self.max_frames)
            print(f"ℹ️ Processing animated GIF with {frame_count} frames (PIL)")
            
            all_predictions = []
            
            for frame_idx in range(frame_count):
                try:
                    gif.seek(frame_idx)
                    frame = gif.convert('RGB')
                    
                    resized = frame.resize(
                        (self.image_dim, self.image_dim),
                        Image.BICUBIC
                    )
                    
                    img_array = np.array(resized, dtype=np.float32) / 255.0
                    img_array = np.expand_dims(img_array, axis=0)
                    
                    predictions = self.predict_fn(img_array)
                    all_predictions.append(predictions)
                    
                    del frame, resized, img_array
                    
                    if frame_idx % 10 == 0:
                        gc.collect()
                        
                except Exception as e:
                    print(f"⚠️ Error processing frame {frame_idx}: {e}")
                    continue
            
            if not all_predictions:
                return None
            
            avg_predictions = np.mean(all_predictions, axis=0)
            print(f"✅ PIL GIF processing complete: Averaged {len(all_predictions)} frames")
            return self._format_predictions(avg_predictions)
            
        except Exception as e:
            print(f"⚠️ Animated PIL processing failed: {e}")
            return None
    
    def _try_opencv_method(self, gif_path: str) -> Optional[Dict[str, float]]:
        """Method 2: OpenCV as fallback"""
        try:
            import cv2
            
            print("🔄 Trying OpenCV method for GIF...")
            cap = cv2.VideoCapture(gif_path)
            
            if not cap.isOpened():
                print("⚠️ OpenCV cannot open GIF")
                cap.release()
                return None
            
            frames = []
            frame_count = 0
            
            while frame_count < self.max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
                frame_count += 1
            
            cap.release()
            
            if not frames:
                print("⚠️ OpenCV: No frames extracted")
                return None
            
            print(f"ℹ️ Processing {len(frames)} frames (OpenCV)")
            
            all_predictions = []
            for frame in frames:
                resized = frame.resize((self.image_dim, self.image_dim), Image.BICUBIC)
                img_array = np.array(resized, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                predictions = self.predict_fn(img_array)
                all_predictions.append(predictions)
                del frame, resized, img_array
                gc.collect()
            
            if not all_predictions:
                return None
            
            avg_predictions = np.mean(all_predictions, axis=0)
            print(f"✅ OpenCV GIF processing complete: Averaged {len(all_predictions)} frames")
            return self._format_predictions(avg_predictions)
            
        except ImportError:
            print("⚠️ OpenCV is not installed")
            return None
        except Exception as e:
            print(f"⚠️ OpenCV method failed: {e}")
            return None
    
    def _try_imageio_method(self, gif_path: str) -> Optional[Dict[str, float]]:
        """Method 3: imageio as fallback"""
        try:
            import imageio.v2 as imageio
            
            print("🔄 Trying imageio method for GIF...")
            frames = imageio.mimread(gif_path, memtest=False)
            
            if not frames:
                print("⚠️ imageio: No frames extracted")
                return None
            
            frames = frames[:self.max_frames]
            print(f"ℹ️ Processing {len(frames)} frames (imageio)")
            
            all_predictions = []
            for frame in frames:
                # Convert to RGB if needed
                if len(frame.shape) == 2:
                    frame = np.stack([frame]*3, axis=-1)
                elif frame.shape[2] == 4:
                    frame = frame[:, :, :3]
                
                pil_image = Image.fromarray(frame)
                resized = pil_image.resize((self.image_dim, self.image_dim), Image.BICUBIC)
                img_array = np.array(resized, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                predictions = self.predict_fn(img_array)
                all_predictions.append(predictions)
                del frame, pil_image, resized, img_array
                gc.collect()
            
            if not all_predictions:
                return None
            
            avg_predictions = np.mean(all_predictions, axis=0)
            print(f"✅ imageio GIF processing complete: Averaged {len(all_predictions)} frames")
            return self._format_predictions(avg_predictions)
            
        except ImportError:
            print("⚠️ imageio is not installed")
            return None
        except Exception as e:
            print(f"⚠️ imageio method failed: {e}")
            return None
    
    def _try_bytes_method(self, gif_path: str) -> Optional[Dict[str, float]]:
        """Method 4: Read as bytes and process"""
        try:
            print("🔄 Trying bytes method for GIF...")
            
            with open(gif_path, 'rb') as f:
                content = f.read()
            
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(content))
            image.seek(0)
            frame = image.convert('RGB')
            
            resized = frame.resize((self.image_dim, self.image_dim), Image.BICUBIC)
            img_array = np.array(resized, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            predictions = self.predict_fn(img_array)
            
            print("✅ Bytes method GIF processing complete: Single frame")
            return self._format_predictions(predictions)
            
        except Exception as e:
            print(f"⚠️ Bytes method failed: {e}")
            return None
    
    def _format_predictions(self, predictions: np.ndarray) -> Dict[str, float]:
        """Convert predictions to dictionary"""
        categories = ['drawing', 'hentai', 'neutral', 'porn', 'sexy']
        return {
            category: round(float(predictions[i]), 8)
            for i, category in enumerate(categories)
        }
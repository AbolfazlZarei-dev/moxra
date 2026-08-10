# -*- coding: utf-8 -*-
"""
Moxra - Video Processor
"""

import os
import gc
from typing import Optional, Dict, Callable, List
import cv2
import numpy as np
from PIL import Image

from ..core.config import Config


class VideoProcessor:
    """
    Video file processor for NSFW content detection
    
    Supports: MP4, AVI, MOV, MKV, WMV, FLV, WEBM
    """
    
    def __init__(self, config: Config, predict_fn: Callable):
        self.config = config
        self.image_dim = config.image_dim
        self.predict_fn = predict_fn
        self.max_frames = 500  # Frame limit for performance
    
    def process(self, video_path: str, 
                sample_rate: float = 0.1,
                max_frames: Optional[int] = None) -> Optional[Dict]:
        """
        Process video file
        
        Args:
            video_path: Path to video file
            sample_rate: Frame sampling rate (0 to 1)
            max_frames: Maximum frames to process
        
        Returns:
            Dictionary with average predictions and frame details
        """
        cap = None
        try:
            # Check file size
            if os.path.getsize(video_path) > 100 * 1024 * 1024:
                raise ValueError("Video file too large: maximum 100 MB")
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if total_frames <= 0:
                raise ValueError("Video has no frames")
            
            # Calculate frame interval
            if sample_rate <= 0 or sample_rate > 1:
                sample_rate = 0.1
            frame_interval = max(1, int(1 / sample_rate))
            
            # Limit frames
            max_allowed = min(max_frames or self.max_frames, self.max_frames)
            frames_to_process = min(total_frames, max_allowed * frame_interval)
            
            all_predictions = []
            frame_scores = []
            
            print(f"📹 Processing video: {total_frames} frames, sampling every {frame_interval} frames")
            
            processed_count = 0
            for frame_idx in range(0, int(frames_to_process), frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize
                resized = pil_image.resize(
                    (self.image_dim, self.image_dim),
                    Image.BICUBIC
                )
                
                # Convert to array
                img_array = np.array(resized, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                # Detect
                predictions = self.predict_fn(img_array)
                all_predictions.append(predictions)
                
                # Record frame score
                timestamp = frame_idx / fps if fps > 0 else frame_idx
                frame_scores.append({
                    'time': round(timestamp, 2),
                    'predictions': self._format_predictions(predictions)
                })
                
                processed_count += 1
                
                # Show progress
                if processed_count % 10 == 0:
                    print(f"\r   Processed: {processed_count} frames", end="")
                
                # Cleanup memory
                del frame, frame_rgb, pil_image, resized, img_array
                
                # Periodic cleanup
                if processed_count % 50 == 0:
                    gc.collect()
            
            print()  # New line after progress display
            
            cap.release()
            
            if not all_predictions:
                return None
            
            # Average predictions
            avg_predictions = np.mean(all_predictions, axis=0)
            
            return {
                'average': self._format_predictions(avg_predictions),
                'frames': frame_scores,
                'metadata': {
                    'total_frames': total_frames,
                    'processed_frames': len(all_predictions),
                    'fps': fps,
                    'duration': total_frames / fps if fps > 0 else 0,
                    'sample_rate': sample_rate,
                    'resolution': f"{width}x{height}"
                }
            }
        
        except Exception as e:
            print(f"Error processing video: {e}")
            if cap:
                cap.release()
            return None
    
    def _format_predictions(self, predictions: np.ndarray) -> Dict[str, float]:
        """
        Convert predictions to dictionary
        
        Args:
            predictions: Predictions array
        
        Returns:
            Dictionary of categories with rounded values
        """
        categories = ['drawing', 'hentai', 'neutral', 'porn', 'sexy']
        return {
            category: round(float(predictions[i]), 8)
            for i, category in enumerate(categories)
        }
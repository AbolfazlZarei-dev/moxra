# -*- coding: utf-8 -*-
"""
Moxra - Core Detection Engine
"""

import os
import gc
import time
from typing import Dict, Optional, List, Any
import threading

import numpy as np
import onnxruntime as ort

from .config import Config, CATEGORIES, MODEL_TYPES, NSFW_WEIGHTS
from .models import ModelManager
from ..processors.image import ImageProcessor
from ..processors.gif import GIFProcessor
from ..processors.video import VideoProcessor


class MoxraDetector:
    """
    Moxra Main Detection Engine for NSFW Content
    
    Features:
        - Detection in images, GIFs, and videos
        - ONNX Runtime with GPU support
        - Automatic model management
        - Async processing support
        - Thread-safe execution
        - Veil/Hijab detection for Islamic content
        - False positive reduction
    
    Example:
        >>> detector = MoxraDetector()
        >>> result = detector.classify_with_veil("image.jpg")
        >>> print(result)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the detection engine
        
        Args:
            config: Configuration object, uses Config.from_env() if None
        """
        self.config = config or Config.from_env()
        self.model_manager = ModelManager(self.config)
        self._lock = threading.Lock()
        
        # Get thresholds from config
        self.NSFW_THRESHOLD = self.config.nsfw_threshold
        self.SAFE_THRESHOLD = self.config.safe_threshold
        self.SUSPICIOUS_THRESHOLD = self.config.suspicious_threshold
        
        # Initialize processors
        self.image_processor = ImageProcessor(self.config)
        self.gif_processor = GIFProcessor(self.config, self._predict_single)
        self.video_processor = VideoProcessor(self.config, self._predict_single)
        
        # Load model
        self._load_model()
        
        # Statistics
        self.inference_count = 0
        self.error_count = 0
        self.start_time = time.time()
    
    def _load_model(self):
        """Load ONNX model"""
        model_path = self.model_manager.get_model_path(self.config.model_type)
        model_config = MODEL_TYPES.get(self.config.model_type)
        
        if model_config:
            self.image_dim = model_config.dim
        else:
            self.image_dim = 224
        
        self.categories = CATEGORIES
        
        # Get providers
        providers = self._get_providers()
        
        # Session options
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.enable_mem_pattern = True
        sess_options.enable_cpu_mem_arena = True
        sess_options.enable_mem_reuse = True
        sess_options.intra_op_num_threads = self.config.intra_threads
        sess_options.inter_op_num_threads = self.config.inter_threads
        
        # Provider options
        provider_options = self._get_provider_options(providers)
        
        # Create session
        self.session = ort.InferenceSession(
            model_path,
            sess_options,
            providers=providers,
            provider_options=provider_options
        )
        
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [out.name for out in self.session.get_outputs()]
        
        print(f"✅ Model loaded: {model_path}")
        print(f"   Input: {self.input_name}, Outputs: {self.output_names}")
        print(f"   Providers: {providers}")
        print(f"   Image dimensions: {self.image_dim}x{self.image_dim}")
        print(f"   Thresholds: NSFW={self.NSFW_THRESHOLD}, Safe={self.SAFE_THRESHOLD}")
    
    def _get_providers(self) -> List[str]:
        """Get execution providers"""
        available = ort.get_available_providers()
        providers = []
        
        device_map = {
            'cpu': [],
            'cuda': ['CUDAExecutionProvider'],
            'tensorrt': ['TensorrtExecutionProvider', 'CUDAExecutionProvider'],
            'dml': ['DmlExecutionProvider'],
            'coreml': ['CoreMLExecutionProvider'],
            'openvino': ['OpenVINOExecutionProvider'],
            'auto': [
                'TensorrtExecutionProvider',
                'CUDAExecutionProvider',
                'DmlExecutionProvider',
                'CoreMLExecutionProvider',
                'OpenVINOExecutionProvider'
            ]
        }
        
        device = self.config.device.lower()
        if device in device_map:
            for provider in device_map[device]:
                if provider in available:
                    providers.append(provider)
        
        if 'CPUExecutionProvider' not in providers:
            providers.append('CPUExecutionProvider')
        
        return providers
    
    def _get_provider_options(self, providers: List[str]) -> List[Dict]:
        """Get provider options with memory limits"""
        options_list = []
        
        for provider in providers:
            opts = {}
            
            if provider == 'CUDAExecutionProvider':
                gpu_limit = os.environ.get("MOXRA_GPU_MEM_LIMIT")
                opts['gpu_mem_limit'] = int(gpu_limit) if gpu_limit else 500 * 1024 * 1024
                opts['arena_extend_strategy'] = 'kSameAsRequested'
                opts['enable_cuda_graph'] = False
                opts['cudnn_conv_algo_search'] = 'HEURISTIC'
            
            elif provider == 'TensorrtExecutionProvider':
                trt_workspace = os.environ.get("MOXRA_TRT_MAX_WORKSPACE")
                opts['trt_max_workspace_size'] = int(trt_workspace) if trt_workspace else 1 * 1024 * 1024 * 1024
                opts['trt_max_cached_engines'] = 1
            
            options_list.append(opts)
        
        return options_list
    
    def _predict_single(self, image: np.ndarray) -> np.ndarray:
        """Run a single inference (thread-safe)"""
        with self._lock:
            outputs = self.session.run(
                self.output_names,
                {self.input_name: image}
            )
            result = outputs[0][0].copy()
            
            self.inference_count += 1
            
            # Periodic cleanup
            if self.config.cleanup_interval > 0 and \
               self.inference_count % self.config.cleanup_interval == 0:
                gc.collect()
            
            return result
    
    def _format_predictions(self, predictions: np.ndarray) -> Dict[str, float]:
        """Convert predictions to dictionary"""
        return {
            category: round(float(predictions[i]), 8)
            for i, category in enumerate(self.categories)
        }
    
    def _calculate_nsfw_score(self, predictions: Dict[str, float]) -> float:
        """
        Calculate NSFW score with proper weighting
        
        Weights from NSFW_WEIGHTS:
        - porn: 1.0 (Explicitly NSFW)
        - hentai: 0.85 (Anime NSFW)
        - sexy: 0.25 (Provocative - lower weight to reduce false positives)
        - drawing: 0.02 (Drawing - usually safe)
        - neutral: 0.0 (Safe)
        
        New rule: If neutral has the highest probability, reduce NSFW score
        """
        score = 0.0
        for category, prob in predictions.items():
            score += prob * NSFW_WEIGHTS.get(category, 0.0)
        
        # If neutral is the highest probability, reduce score
        max_category = max(predictions, key=predictions.get)
        max_prob = predictions[max_category]
        neutral_prob = predictions.get("neutral", 0)
        
        if max_category == "neutral":
            # Model believes content is safe
            reduction_factor = 0.3  # Only 30% of score is retained
            score = score * reduction_factor
            print(f"🟢 Dominant category neutral ({neutral_prob:.3f}), reduced NSFW score by {int((1-reduction_factor)*100)}%")
        
        elif neutral_prob > 0.5:
            # Even if neutral isn't highest, but above 50%
            reduction_factor = 0.5
            score = score * reduction_factor
            print(f"🟢 High neutral probability ({neutral_prob:.3f}), reduced NSFW score by {int((1-reduction_factor)*100)}%")
        
        # If sexy is highest but neutral is also high
        # Could be normal content with touching (like hugging)
        if max_category == "sexy" and neutral_prob > 0.3:
            ratio = max_prob / max(neutral_prob, 0.01)
            if ratio < 2.0:  # If sexy isn't much higher than neutral
                reduction_factor = 0.6
                score = score * reduction_factor
                print(f"🟡 Ambiguous content (sexy={max_prob:.3f}, neutral={neutral_prob:.3f}), reducing score")
        
        # Normalize (limit to 0-1)
        return min(1.0, max(0.0, score))
    
    def _detect_veil(self, image_path: str) -> Dict[str, Any]:
        """
        Approximate veil/hijab detection by checking dark colors in head area
        
        Returns:
            Dictionary with veil detection information
        """
        try:
            import cv2
            
            img = cv2.imread(image_path)
            if img is None:
                return {"has_veil": False, "confidence": 0.0, "method": "none"}
            
            height, width = img.shape[:2]
            
            # Head area (top third of image, center)
            head_y1 = 0
            head_y2 = int(height * 0.35)
            head_x1 = int(width * 0.2)
            head_x2 = int(width * 0.8)
            
            head_region = img[head_y1:head_y2, head_x1:head_x2]
            
            if head_region.size == 0:
                return {"has_veil": False, "confidence": 0.0, "method": "none"}
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(head_region, cv2.COLOR_BGR2HSV)
            
            # Detect dark colors (black, dark brown, navy, dark blue)
            dark_mask1 = cv2.inRange(hsv, (0, 0, 0), (180, 255, 40))
            dark_mask2 = cv2.inRange(hsv, (0, 0, 40), (180, 255, 60))
            dark_mask = cv2.bitwise_or(dark_mask1, dark_mask2)
            
            dark_ratio = np.sum(dark_mask > 0) / dark_mask.size
            
            # Detect light colors (for white hijab)
            light_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
            light_ratio = np.sum(light_mask > 0) / light_mask.size
            
            # Detect pure black (chador/abaya)
            black_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 30))
            black_ratio = np.sum(black_mask > 0) / black_mask.size
            
            # Combine criteria
            veil_score = 0.0
            method = "none"
            
            # If more than 35% of head area is dark
            if dark_ratio > 0.35:
                veil_score += dark_ratio
                method = "dark"
            
            # If more than 30% of head area is light (white hijab)
            if light_ratio > 0.30:
                veil_score += light_ratio * 0.5
                method = "light" if method == "none" else "mixed"
            
            # If more than 20% of head area is pure black (chador)
            if black_ratio > 0.20:
                veil_score += black_ratio * 1.2
                method = "black" if method == "none" else "mixed"
            
            # Normalize
            veil_score = min(1.0, veil_score)
            
            # Veil detection threshold
            has_veil = veil_score > 0.30
            
            return {
                "has_veil": has_veil,
                "confidence": round(veil_score, 3),
                "dark_ratio": round(dark_ratio, 3),
                "light_ratio": round(light_ratio, 3),
                "black_ratio": round(black_ratio, 3),
                "method": method
            }
        
        except Exception as e:
            print(f"⚠️ Veil detection error: {e}")
            return {"has_veil": False, "confidence": 0.0, "method": "error"}
    
    def classify_with_veil(self, image_path: str) -> Optional[Dict]:
        """
        NSFW detection with veil consideration
        
        Returns:
            Complete dictionary including predictions, scores, and veil information
        """
        predictions = self.predict_image(image_path)
        if not predictions:
            return None
        
        # Calculate NSFW score
        raw_score = self._calculate_nsfw_score(predictions)
        
        # Detect veil
        veil_info = self._detect_veil(image_path)
        
        # Adjust final score based on veil
        adjusted_score = raw_score
        if veil_info["has_veil"]:
            reduction = 0.3 * veil_info["confidence"]
            adjusted_score = max(0.0, raw_score - reduction)
            print(f"🕊️ Veil detected: Score reduced from {raw_score:.3f} to {adjusted_score:.3f}")
        
        # Apply thresholds
        is_nsfw = adjusted_score >= self.NSFW_THRESHOLD
        is_safe = adjusted_score <= self.SAFE_THRESHOLD
        is_suspicious = self.SAFE_THRESHOLD < adjusted_score < self.NSFW_THRESHOLD
        
        print(f"📊 Score analysis:")
        print(f"   Predictions: {predictions}")
        print(f"   Dominant category: {max(predictions, key=predictions.get)}")
        print(f"   Raw NSFW score: {raw_score:.4f}")
        print(f"   Final score: {adjusted_score:.4f}")
        print(f"   Thresholds: NSFW≥{self.NSFW_THRESHOLD}, Safe≤{self.SAFE_THRESHOLD}")
        print(f"   Result: {'NSFW' if is_nsfw else 'SAFE' if is_safe else 'SUSPICIOUS'}")
        
        return {
            "predictions": predictions,
            "raw_nsfw_score": raw_score,
            "adjusted_nsfw_score": adjusted_score,
            "is_nsfw": is_nsfw,
            "is_safe": is_safe,
            "is_suspicious": is_suspicious,
            "veil": veil_info,
            "thresholds": {
                "nsfw": self.NSFW_THRESHOLD,
                "safe": self.SAFE_THRESHOLD,
                "suspicious": self.SUSPICIOUS_THRESHOLD
            },
            "dominant_category": max(predictions, key=predictions.get)
        }
    
    # ========== Public Methods ==========
    
    def predict_image(self, image_path: str) -> Optional[Dict[str, float]]:
        """
        Detect NSFW content in an image
        
        Args:
            image_path: Path to image file (JPG, PNG, WEBP, BMP)
        
        Returns:
            Dictionary of category probabilities
        """
        if not os.path.exists(image_path):
            raise ValueError(f"Image not found: {image_path}")
        
        try:
            print(f"🔍 Processing image: {image_path}")
            result = self.image_processor.process(image_path)
            if result is None:
                return None
            
            predictions = self._predict_single(result)
            return self._format_predictions(predictions)
        
        except Exception as e:
            self.error_count += 1
            print(f"❌ Image detection failed: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Detection failed: {e}")
    
    def predict_gif(self, gif_path: str) -> Optional[Dict[str, float]]:
        """
        Detect NSFW content in a GIF
        
        Args:
            gif_path: Path to GIF file
        
        Returns:
            Dictionary of category probabilities (averaged across frames)
        """
        if not os.path.exists(gif_path):
            raise ValueError(f"GIF not found: {gif_path}")
        
        try:
            print(f"🔍 Processing GIF: {gif_path}")
            result = self.gif_processor.process(gif_path)
            
            if result is None:
                print("⚠️ GIF processor returned None, trying image processing...")
                result = self.predict_image(gif_path)
            
            return result
        
        except Exception as e:
            self.error_count += 1
            print(f"❌ GIF processing failed: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"GIF processing failed: {e}")
    
    def predict_video(self, video_path: str, 
                      sample_rate: float = 0.1,
                      max_frames: Optional[int] = None) -> Optional[Dict]:
        """
        Detect NSFW content in a video
        
        Args:
            video_path: Path to video file
            sample_rate: Frame sampling rate (0 to 1), default 0.1
            max_frames: Maximum frames to process, None = no limit
        
        Returns:
            Dictionary with average predictions and frame details
        """
        if not os.path.exists(video_path):
            raise ValueError(f"Video not found: {video_path}")
        
        try:
            return self.video_processor.process(
                video_path,
                sample_rate=sample_rate,
                max_frames=max_frames
            )
        
        except Exception as e:
            self.error_count += 1
            raise RuntimeError(f"Video processing failed: {e}")
    
    def predict_bytes(self, image_bytes: bytes) -> Optional[Dict[str, float]]:
        """
        Detect NSFW content from binary image data
        
        Args:
            image_bytes: Image data as bytes
        
        Returns:
            Dictionary of category probabilities
        """
        try:
            result = self.image_processor.process_bytes(image_bytes)
            if result is None:
                return None
            
            predictions = self._predict_single(result)
            return self._format_predictions(predictions)
        
        except Exception as e:
            self.error_count += 1
            raise RuntimeError(f"Byte processing failed: {e}")
    
    def predict_with_score(self, image_path: str) -> Optional[Dict]:
        """
        Detect NSFW content with additional score (legacy - use classify_with_veil)
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with predictions, NSFW score, and category
        """
        return self.classify_with_veil(image_path)
    
    def get_stats(self) -> Dict:
        """Get detection statistics"""
        uptime = time.time() - self.start_time
        return {
            "inference_count": self.inference_count,
            "error_count": self.error_count,
            "device": self.config.device,
            "image_dim": self.image_dim,
            "cleanup_interval": self.config.cleanup_interval,
            "uptime_seconds": round(uptime, 2),
            "provider": str(self.session.get_providers()),
            "model_type": self.config.model_type,
            "thresholds": {
                "nsfw": self.NSFW_THRESHOLD,
                "safe": self.SAFE_THRESHOLD,
                "suspicious": self.SUSPICIOUS_THRESHOLD
            }
        }
    
    def cleanup(self):
        """Clean up resources"""
        gc.collect()
        if hasattr(self, 'session'):
            del self.session
        gc.collect()
    
    # ========== Async Methods ==========
    
    async def predict_image_async(self, image_path: str) -> Optional[Dict[str, float]]:
        """Async version of predict_image"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.predict_image, image_path
            )
    
    async def predict_gif_async(self, gif_path: str) -> Optional[Dict[str, float]]:
        """Async version of predict_gif"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.predict_gif, gif_path
            )
    
    async def predict_video_async(self, video_path: str,
                                   sample_rate: float = 0.1,
                                   max_frames: Optional[int] = None) -> Optional[Dict]:
        """Async version of predict_video"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.predict_video, video_path, sample_rate, max_frames
            )
    
    async def predict_bytes_async(self, image_bytes: bytes) -> Optional[Dict[str, float]]:
        """Async version of predict_bytes"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.predict_bytes, image_bytes
            )
    
    async def classify_with_veil_async(self, image_path: str) -> Optional[Dict]:
        """Async version of classify_with_veil"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.classify_with_veil, image_path
            )
# -*- coding: utf-8 -*-
"""
Moxra - API Routes
"""

import os
import gc
import tempfile
from typing import Dict, Any
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
import requests
import cv2
import numpy as np

from ..core.detector import MoxraDetector
from ..core.config import Config


def get_detector() -> MoxraDetector:
    """Get detector instance"""
    config = Config.from_env()
    return MoxraDetector(config)


router = APIRouter(prefix="/api/v1", tags=["Moxra"])


# Helper functions

def convert_numpy_to_python(obj):
    """
    Convert all numpy values to Python native types for JSON
    
    Args:
        obj: Input object (can be numpy or Python native)
    
    Returns:
        Object converted to Python native
    """
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_to_python(item) for item in obj)
    return obj


def clean_response(data: dict) -> dict:
    """
    Clean response dictionary from numpy values
    
    Args:
        data: Response dictionary
    
    Returns:
        Cleaned dictionary
    """
    return convert_numpy_to_python(data)


# Image classification

@router.post("/classify-img")
async def classify_image(
    image: UploadFile = File(...),
    detector: MoxraDetector = Depends(get_detector)
):
    """
    Detect inappropriate content in uploaded image
    
    Features:
        - Public access - No authentication required
        - Supports: JPG, PNG, WEBP, BMP
        - Maximum size: 20 MB
    """
    temp_path = None
    try:
        # Check file type
        valid_types = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp']
        if image.content_type not in valid_types:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {image.content_type}. Allowed formats: JPG, PNG, WEBP, BMP"
            )
        
        # Create upload directory
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save temporary file
        temp_path = upload_dir / image.filename
        content = await image.read()
        
        # Check file size
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File too large: maximum 20 MB"
            )
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Detect with veil consideration
        result = detector.classify_with_veil(str(temp_path))
        
        if not result:
            raise HTTPException(status_code=500, detail="Detection failed")
        
        # Build response
        response_data = {
            "Moxra": {
                "model": "Moxra-1",
                "ok": not result["is_nsfw"],
                "channel": "https://rubika.ir/Ninja_Code",
                "writer": " https://abolfazlzarei.sbs ",
                "result": {
                    "filename": image.filename,
                    "type": "image",
                    "predictions": result["predictions"],
                    "dominant_category": result.get("dominant_category", ""),
                    "raw_nsfw_score": float(result["raw_nsfw_score"]),
                    "adjusted_nsfw_score": float(result["adjusted_nsfw_score"]),
                    "is_nsfw": bool(result["is_nsfw"]),
                    "is_safe": bool(result["is_safe"]),
                    "is_suspicious": bool(result["is_suspicious"]),
                    "veil": {
                        "has_veil": bool(result["veil"]["has_veil"]),
                        "confidence": float(result["veil"]["confidence"]),
                        "dark_ratio": float(result["veil"].get("dark_ratio", 0)),
                        "light_ratio": float(result["veil"].get("light_ratio", 0)),
                        "black_ratio": float(result["veil"].get("black_ratio", 0)),
                        "method": str(result["veil"].get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(result["thresholds"]["nsfw"]),
                        "safe": float(result["thresholds"]["safe"]),
                        "suspicious": float(result["thresholds"]["suspicious"])
                    }
                }
            }
        }
        
        return clean_response(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Delete temporary file
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
        gc.collect()


# GIF classification

@router.post("/classify-gif")
async def classify_gif(
    gif: UploadFile = File(...),
    detector: MoxraDetector = Depends(get_detector)
):
    """
    Detect inappropriate content in uploaded GIF
    
    Features:
        - Public access - No authentication required
        - Supports: GIF
        - Maximum size: 20 MB
    """
    temp_path = None
    try:
        content_type = gif.content_type or ""
        filename = gif.filename or "file.gif"
        
        # Ensure correct extension
        if not filename.lower().endswith('.gif'):
            filename += '.gif'
        
        print(f"📁 Received GIF: {filename}, content type: {content_type}")
        
        # Create upload directory
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save temporary file
        temp_path = upload_dir / filename
        content = await gif.read()
        
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File too large: maximum 20 MB"
            )
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        print(f"📁 GIF saved: {temp_path}, size: {len(content)} bytes")
        
        # Detect GIF
        try:
            gif_result = detector.predict_gif(str(temp_path))
            
            if gif_result:
                raw_score = detector._calculate_nsfw_score(gif_result)
                veil_info = detector._detect_veil(str(temp_path))
                
                adjusted_score = raw_score
                if veil_info.get("has_veil", False):
                    reduction = 0.3 * veil_info.get("confidence", 0.0)
                    adjusted_score = max(0.0, raw_score - reduction)
                
                is_nsfw = adjusted_score >= detector.NSFW_THRESHOLD
                is_safe = adjusted_score <= detector.SAFE_THRESHOLD
                is_suspicious = detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD
                
                result = {
                    "predictions": gif_result,
                    "raw_nsfw_score": raw_score,
                    "adjusted_nsfw_score": adjusted_score,
                    "is_nsfw": is_nsfw,
                    "is_safe": is_safe,
                    "is_suspicious": is_suspicious,
                    "veil": veil_info,
                    "thresholds": {
                        "nsfw": detector.NSFW_THRESHOLD,
                        "safe": detector.SAFE_THRESHOLD,
                        "suspicious": detector.SUSPICIOUS_THRESHOLD
                    },
                    "dominant_category": max(gif_result, key=gif_result.get)
                }
            else:
                raise ValueError("GIF processing returned no results")
                
        except Exception as e:
            print(f"⚠️ GIF processing failed: {e}, trying alternative methods...")
            
            result = None
            try:
                # Alternative method: Extract frames with OpenCV
                cap = cv2.VideoCapture(str(temp_path))
                frames_data = []
                
                while len(frames_data) < 10:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    temp_frame_path = temp_path.parent / f"temp_frame_{len(frames_data)}.jpg"
                    cv2.imwrite(str(temp_frame_path), frame)
                    
                    frame_result = detector.predict_image(str(temp_frame_path))
                    if frame_result:
                        frames_data.append(frame_result)
                    
                    if temp_frame_path.exists():
                        temp_frame_path.unlink()
                
                cap.release()
                
                if frames_data:
                    avg_predictions = {}
                    for cat in frames_data[0].keys():
                        avg_predictions[cat] = np.mean([f[cat] for f in frames_data])
                    
                    raw_score = detector._calculate_nsfw_score(avg_predictions)
                    veil_info = detector._detect_veil(str(temp_path))
                    
                    adjusted_score = raw_score
                    if veil_info.get("has_veil", False):
                        reduction = 0.3 * veil_info.get("confidence", 0.0)
                        adjusted_score = max(0.0, raw_score - reduction)
                    
                    result = {
                        "predictions": {k: float(v) for k, v in avg_predictions.items()},
                        "raw_nsfw_score": raw_score,
                        "adjusted_nsfw_score": adjusted_score,
                        "is_nsfw": adjusted_score >= detector.NSFW_THRESHOLD,
                        "is_safe": adjusted_score <= detector.SAFE_THRESHOLD,
                        "is_suspicious": detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD,
                        "veil": veil_info,
                        "thresholds": {
                            "nsfw": detector.NSFW_THRESHOLD,
                            "safe": detector.SAFE_THRESHOLD,
                            "suspicious": detector.SUSPICIOUS_THRESHOLD
                        },
                        "dominant_category": max(avg_predictions, key=avg_predictions.get)
                    }
            except Exception as e2:
                print(f"⚠️ OpenCV alternative method also failed: {e2}")
            
            if not result:
                raise HTTPException(status_code=500, detail="GIF processing failed with all methods")
        
        print(f"📊 GIF results:")
        print(f"   Dominant category: {result.get('dominant_category')}")
        print(f"   Raw score: {result['raw_nsfw_score']:.3f}")
        print(f"   Final score: {result['adjusted_nsfw_score']:.3f}")
        print(f"   NSFW: {result['is_nsfw']}")
        
        response_data = {
            "Moxra": {
                "model": "Moxra-1",
                "ok": not result["is_nsfw"],
                "channel": "https://rubika.ir/Ninja_Code",
                "writer": " https://abolfazlzarei.sbs ",
                "result": {
                    "filename": filename,
                    "type": "gif",
                    "predictions": result["predictions"],
                    "dominant_category": result.get("dominant_category", ""),
                    "raw_nsfw_score": float(result["raw_nsfw_score"]),
                    "adjusted_nsfw_score": float(result["adjusted_nsfw_score"]),
                    "is_nsfw": bool(result["is_nsfw"]),
                    "is_safe": bool(result["is_safe"]),
                    "is_suspicious": bool(result["is_suspicious"]),
                    "veil": {
                        "has_veil": bool(result["veil"]["has_veil"]),
                        "confidence": float(result["veil"]["confidence"]),
                        "dark_ratio": float(result["veil"].get("dark_ratio", 0)),
                        "light_ratio": float(result["veil"].get("light_ratio", 0)),
                        "black_ratio": float(result["veil"].get("black_ratio", 0)),
                        "method": str(result["veil"].get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(result["thresholds"]["nsfw"]),
                        "safe": float(result["thresholds"]["safe"]),
                        "suspicious": float(result["thresholds"]["suspicious"])
                    }
                }
            }
        }
        
        return clean_response(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ GIF detection error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
        gc.collect()


# Video classification

@router.post("/classify-video")
async def classify_video(
    video: UploadFile = File(...),
    sample_rate: float = Form(0.1),
    max_frames: int = Form(None),
    detector: MoxraDetector = Depends(get_detector)
):
    """
    Detect inappropriate content in uploaded video
    
    Features:
        - Public access - No authentication required
        - Supports: MP4, AVI, MOV, MKV, WMV, FLV, WEBM
        - Maximum size: 100 MB
    """
    temp_path = None
    try:
        # Check video format
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        ext = os.path.splitext(video.filename)[1].lower()
        if ext not in video_exts:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported video format: {ext}. Allowed formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM"
            )
        
        # Create upload directory
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save temporary file
        temp_path = upload_dir / video.filename
        content = await video.read()
        
        if len(content) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Video too large: maximum 100 MB"
            )
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Process video
        video_result = await detector.predict_video_async(
            str(temp_path),
            sample_rate=sample_rate,
            max_frames=max_frames
        )
        
        if not video_result:
            raise HTTPException(status_code=500, detail="Video processing failed")
        
        avg_predictions = video_result.get("average", {})
        raw_score = detector._calculate_nsfw_score(avg_predictions)
        
        # Detect veil in first frame
        veil_info = {"has_veil": False, "confidence": 0.0}
        try:
            cap = cv2.VideoCapture(str(temp_path))
            ret, frame = cap.read()
            cap.release()
            if ret:
                temp_frame = temp_path.parent / f"temp_frame_{video.filename}.jpg"
                cv2.imwrite(str(temp_frame), frame)
                veil_info = detector._detect_veil(str(temp_frame))
                if temp_frame.exists():
                    temp_frame.unlink()
        except Exception as e:
            print(f"⚠️ Veil detection in video failed: {e}")
        
        # Adjust score based on veil
        adjusted_score = raw_score
        if veil_info.get("has_veil", False):
            reduction = 0.3 * veil_info.get("confidence", 0.0)
            adjusted_score = max(0.0, raw_score - reduction)
            print(f"🕊️ Veil in video: Score reduced from {raw_score:.3f} to {adjusted_score:.3f}")
        
        # Apply thresholds
        is_nsfw = adjusted_score >= detector.NSFW_THRESHOLD
        is_safe = adjusted_score <= detector.SAFE_THRESHOLD
        is_suspicious = detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD
        
        print(f"📊 Video results:")
        print(f"   Dominant category: {max(avg_predictions, key=avg_predictions.get)}")
        print(f"   Raw score: {raw_score:.3f}")
        print(f"   Final score: {adjusted_score:.3f}")
        print(f"   NSFW: {is_nsfw}")
        
        # Build frames list
        frames_list = []
        for frame in video_result.get("frames", [])[:10]:
            frames_list.append({
                "time": float(frame.get("time", 0)),
                "predictions": {
                    k: float(v) for k, v in frame.get("predictions", {}).items()
                }
            })
        
        response_data = {
            "Moxra": {
                "model": "Moxra-1",
                "ok": not bool(is_nsfw),
                "channel": "https://rubika.ir/Ninja_Code",
                "writer": " https://abolfazlzarei.sbs ",
                "result": {
                    "filename": video.filename,
                    "type": "video",
                    "predictions": {k: float(v) for k, v in avg_predictions.items()},
                    "dominant_category": str(max(avg_predictions, key=avg_predictions.get)),
                    "raw_nsfw_score": float(raw_score),
                    "adjusted_nsfw_score": float(adjusted_score),
                    "is_nsfw": bool(is_nsfw),
                    "is_safe": bool(is_safe),
                    "is_suspicious": bool(is_suspicious),
                    "veil": {
                        "has_veil": bool(veil_info.get("has_veil", False)),
                        "confidence": float(veil_info.get("confidence", 0.0)),
                        "dark_ratio": float(veil_info.get("dark_ratio", 0)),
                        "light_ratio": float(veil_info.get("light_ratio", 0)),
                        "black_ratio": float(veil_info.get("black_ratio", 0)),
                        "method": str(veil_info.get("method", "none"))
                    },
                    "frames": frames_list,
                    "metadata": {
                        "total_frames": int(video_result.get("metadata", {}).get("total_frames", 0)),
                        "processed_frames": int(video_result.get("metadata", {}).get("processed_frames", 0)),
                        "fps": float(video_result.get("metadata", {}).get("fps", 0)),
                        "duration": float(video_result.get("metadata", {}).get("duration", 0)),
                        "sample_rate": float(video_result.get("metadata", {}).get("sample_rate", 0)),
                        "resolution": str(video_result.get("metadata", {}).get("resolution", ""))
                    },
                    "thresholds": {
                        "nsfw": float(detector.NSFW_THRESHOLD),
                        "safe": float(detector.SAFE_THRESHOLD),
                        "suspicious": float(detector.SUSPICIOUS_THRESHOLD)
                    }
                }
            }
        }
        
        return clean_response(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Video error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
        gc.collect()


# URL classification

@router.post("/classify-url")
async def classify_url(
    request: dict,
    detector: MoxraDetector = Depends(get_detector)
):
    """
    Detect inappropriate content via URL
    
    Features:
        - Public access - No authentication required
        - Supports: JPG, PNG, GIF, WEBP, BMP, MP4, AVI, MOV, MKV, WEBM
    """
    temp_file = None
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Download file
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="File download failed"
            )
        
        if len(response.content) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File too large: maximum 100 MB"
            )
        
        # Detect file type
        url_lower = url.lower()
        is_gif = 'gif' in url_lower
        is_video = any(ext in url_lower for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'])
        
        if is_gif:
            ext = 'gif'
            file_type = 'gif'
        elif is_video:
            ext = 'mp4'
            file_type = 'video'
        else:
            ext = 'jpg'
            file_type = 'image'
        
        # Save temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
        temp_file.write(response.content)
        temp_file.close()
        
        result_data = None
        
        # Process based on file type
        if file_type == 'gif':
            gif_result = detector.predict_gif(temp_file.name)
            if gif_result:
                raw_score = detector._calculate_nsfw_score(gif_result)
                veil_info = detector._detect_veil(temp_file.name)
                
                adjusted_score = raw_score
                if veil_info.get("has_veil", False):
                    reduction = 0.3 * veil_info.get("confidence", 0.0)
                    adjusted_score = max(0.0, raw_score - reduction)
                
                result_data = {
                    "predictions": gif_result,
                    "dominant_category": max(gif_result, key=gif_result.get),
                    "raw_nsfw_score": float(raw_score),
                    "adjusted_nsfw_score": float(adjusted_score),
                    "is_nsfw": bool(adjusted_score >= detector.NSFW_THRESHOLD),
                    "is_safe": bool(adjusted_score <= detector.SAFE_THRESHOLD),
                    "is_suspicious": bool(detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD),
                    "veil": {
                        "has_veil": bool(veil_info.get("has_veil", False)),
                        "confidence": float(veil_info.get("confidence", 0.0)),
                        "method": str(veil_info.get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(detector.NSFW_THRESHOLD),
                        "safe": float(detector.SAFE_THRESHOLD),
                        "suspicious": float(detector.SUSPICIOUS_THRESHOLD)
                    }
                }
                
        elif file_type == 'video':
            video_result = detector.predict_video(temp_file.name, sample_rate=0.1, max_frames=100)
            if video_result:
                avg_predictions = video_result.get("average", {})
                raw_score = detector._calculate_nsfw_score(avg_predictions)
                
                veil_info = {"has_veil": False, "confidence": 0.0}
                try:
                    cap = cv2.VideoCapture(temp_file.name)
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        temp_frame = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        cv2.imwrite(temp_frame.name, frame)
                        veil_info = detector._detect_veil(temp_frame.name)
                        temp_frame.close()
                        os.unlink(temp_frame.name)
                except:
                    pass
                
                adjusted_score = raw_score
                if veil_info.get("has_veil", False):
                    reduction = 0.3 * veil_info.get("confidence", 0.0)
                    adjusted_score = max(0.0, raw_score - reduction)
                
                result_data = {
                    "predictions": {k: float(v) for k, v in avg_predictions.items()},
                    "dominant_category": max(avg_predictions, key=avg_predictions.get),
                    "raw_nsfw_score": float(raw_score),
                    "adjusted_nsfw_score": float(adjusted_score),
                    "is_nsfw": bool(adjusted_score >= detector.NSFW_THRESHOLD),
                    "is_safe": bool(adjusted_score <= detector.SAFE_THRESHOLD),
                    "is_suspicious": bool(detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD),
                    "veil": {
                        "has_veil": bool(veil_info.get("has_veil", False)),
                        "confidence": float(veil_info.get("confidence", 0.0)),
                        "method": str(veil_info.get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(detector.NSFW_THRESHOLD),
                        "safe": float(detector.SAFE_THRESHOLD),
                        "suspicious": float(detector.SUSPICIOUS_THRESHOLD)
                    }
                }
        else:
            result = detector.classify_with_veil(temp_file.name)
            if result:
                result_data = {
                    "predictions": result["predictions"],
                    "dominant_category": result.get("dominant_category", ""),
                    "raw_nsfw_score": float(result["raw_nsfw_score"]),
                    "adjusted_nsfw_score": float(result["adjusted_nsfw_score"]),
                    "is_nsfw": bool(result["is_nsfw"]),
                    "is_safe": bool(result["is_safe"]),
                    "is_suspicious": bool(result["is_suspicious"]),
                    "veil": {
                        "has_veil": bool(result["veil"]["has_veil"]),
                        "confidence": float(result["veil"]["confidence"]),
                        "method": str(result["veil"].get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(result["thresholds"]["nsfw"]),
                        "safe": float(result["thresholds"]["safe"]),
                        "suspicious": float(result["thresholds"]["suspicious"])
                    }
                }
        
        if not result_data:
            raise HTTPException(status_code=500, detail="Detection failed")
        
        response_data = {
            "Moxra": {
                "model": "Moxra-1",
                "ok": not result_data.get("is_nsfw", False),
                "channel": "https://rubika.ir/Ninja_Code",
                "writer": " https://abolfazlzarei.sbs ",
                "result": {
                    "filename": url.split('/')[-1],
                    "type": file_type,
                    **result_data
                }
            }
        }
        
        return clean_response(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ URL error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
        gc.collect()


# Health check

@router.get("/health")
async def health_check(
    detector: MoxraDetector = Depends(get_detector)
):
    """
    Service health check - Public (no authentication required)
    
    Returns:
        Service status and statistics
    """
    stats = detector.get_stats()
    
    response_data = {
        "Moxra": {
            "model": "Moxra-1",
            "ok": True,
            "channel": "https://rubika.ir/Ninja_Code",
            "writer": " https://abolfazlzarei.sbs ",
            "status": "healthy",
            "model_loaded": True,
            "inference_count": int(stats.get("inference_count", 0)),
            "error_count": int(stats.get("error_count", 0)),
            "device": str(stats.get("device", "cpu")),
            "image_dim": int(stats.get("image_dim", 224)),
            "uptime_seconds": float(stats.get("uptime_seconds", 0)),
            "providers": [str(p) for p in stats.get("provider", ["CPUExecutionProvider"])],
            "thresholds": {
                "nsfw": float(stats.get("thresholds", {}).get("nsfw", 0.85)),
                "safe": float(stats.get("thresholds", {}).get("safe", 0.25)),
                "suspicious": float(stats.get("thresholds", {}).get("suspicious", 0.60))
            }
        }
    }
    
    return clean_response(response_data)


# Cache cleanup

@router.post("/cleanup")
async def cleanup_cache(
    detector: MoxraDetector = Depends(get_detector)
):
    """
    Clear cache memory
    
    Features:
        - Public access
        - Clean up resources and memory
    """
    detector.cleanup()
    response_data = {
        "Moxra": {
            "model": "Moxra-1",
            "ok": True,
            "channel": "https://rubika.ir/Ninja_Code",
            "writer": " https://abolfazlzarei.sbs ",
            "status": "success",
            "message": "Cache memory cleared"
        }
    }
    
    return clean_response(response_data)
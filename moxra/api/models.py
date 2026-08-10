# -*- coding: utf-8 -*-
"""
Moxra - API Models (Pydantic V2)
"""

from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class ClassifyRequest(BaseModel):
    """Request model for image classification"""
    image: bytes = Field(..., description="Image data as bytes")


class ClassifyResponse(BaseModel):
    """Response model for image classification"""
    filename: str = Field(..., description="Original filename")
    predictions: Dict[str, float] = Field(..., description="Category probabilities")
    nsfw_score: float = Field(..., description="NSFW score (0 to 1)")
    is_nsfw: bool = Field(..., description="Whether content is inappropriate")
    is_safe: bool = Field(..., description="Whether content is safe")
    is_suspicious: bool = Field(..., description="Whether content is suspicious")
    
    # Using ConfigDict instead of Config class
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "image.jpg",
                "predictions": {
                    "neutral": 0.85,
                    "sexy": 0.08,
                    "porn": 0.04,
                    "hentai": 0.02,
                    "drawing": 0.01
                },
                "nsfw_score": 0.14,
                "is_nsfw": False,
                "is_safe": True,
                "is_suspicious": False
            }
        }
    )


class ClassifyURLRequest(BaseModel):
    """Request model for URL-based classification"""
    url: str = Field(
        ..., 
        description="Image URL",
        json_schema_extra={"example": "https://example.com/image.jpg"}
    )


class VideoClassifyRequest(BaseModel):
    """Request model for video classification"""
    sample_rate: float = Field(
        0.1, 
        description="Frame sampling rate (0 to 1)", 
        ge=0.01, 
        le=1.0
    )
    max_frames: Optional[int] = Field(
        None, 
        description="Maximum frames to process", 
        ge=1, 
        le=1000
    )


class FrameScore(BaseModel):
    """Frame score model"""
    time: float = Field(..., description="Time in seconds")
    predictions: Dict[str, float] = Field(..., description="Category probabilities")


class VideoMetadata(BaseModel):
    """Video metadata model"""
    total_frames: int = Field(..., description="Total number of video frames")
    processed_frames: int = Field(..., description="Number of processed frames")
    fps: float = Field(..., description="Frames per second")
    duration: float = Field(..., description="Video duration in seconds")
    sample_rate: float = Field(..., description="Frame sampling rate")
    resolution: Optional[str] = Field(None, description="Video resolution")


class VideoClassifyResponse(BaseModel):
    """Response model for video classification"""
    average: Dict[str, float] = Field(..., description="Average predictions")
    frames: List[FrameScore] = Field(..., description="Per-frame scores")
    metadata: VideoMetadata = Field(..., description="Video metadata")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    inference_count: int = Field(..., description="Total inference count")
    error_count: int = Field(..., description="Total error count")
    device: str = Field(..., description="Execution device")
    image_dim: int = Field(..., description="Model input dimensions")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    providers: List[str] = Field(..., description="ONNX providers")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    status_code: int = Field(..., description="HTTP status code")
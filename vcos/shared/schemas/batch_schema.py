"""
Shared schemas for batch operations
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class BatchRequest(BaseModel):
    """Request to create a new batch"""
    topic: Optional[str] = None
    cluster: Optional[str] = None
    num_variants: int = 20
    platforms: List[str] = ["tiktok", "instagram", "youtube"]
    metadata: Optional[Dict[str, Any]] = None

class BatchResponse(BaseModel):
    """Response from batch creation"""
    job_id: str
    status: str
    message: str
    created_at: datetime = datetime.now()

class VideoSchema(BaseModel):
    """Video metadata schema"""
    video_id: str
    topic: str
    cluster: str
    hook_type: str
    emotional_angle: str
    length: float
    file_path: str
    created_at: datetime = datetime.now()

class HookSchema(BaseModel):
    """Hook schema"""
    hook_id: str
    template: str
    emotional_angle: str
    curiosity_score: float
    predicted_ctr_score: float
    historical_lift: float = 1.0
    text: str

class AnalyticsSchema(BaseModel):
    """Analytics data schema"""
    video_id: str
    hook_type: str
    emotional_angle: str
    topic_cluster: str
    length: float
    retention_3s: float
    retention_50pct: float
    completion_rate: float
    shares_per_1k: float
    comments_per_1k: float
    velocity_30min: float
    timestamp: datetime = datetime.now()

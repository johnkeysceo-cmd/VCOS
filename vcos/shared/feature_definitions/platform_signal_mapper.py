"""
Platform Signal Mapper
Normalizes different platform metrics into unified signal space
"""

from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class NormalizedSignal:
    """Normalized platform signal"""
    stop_rate: float          # 3s retention
    early_hold: float         # Retention at 25% of video
    mid_hold: float          # Retention at 50% of video
    completion: float        # Completion rate
    save_rate: float         # Saves per 1k views
    share_velocity: float    # Shares per 1k views per hour
    comment_velocity: float  # Comments per 1k views per hour
    view_velocity: float     # Views per minute (first 30min)

def map_tiktok_signal(raw_data: Dict) -> NormalizedSignal:
    """
    Map TikTok API response to normalized signal
    
    Args:
        raw_data: Raw TikTok analytics
        
    Returns:
        NormalizedSignal
    """
    views = raw_data.get("video_views", 1)
    watch_time = raw_data.get("total_watch_time", 0)
    video_duration = raw_data.get("video_duration", 1)
    
    # TikTok specific mappings
    return NormalizedSignal(
        stop_rate=raw_data.get("video_view_rate", {}).get("3s", 0.0),
        early_hold=raw_data.get("video_view_rate", {}).get("25pct", 0.0),
        mid_hold=raw_data.get("video_view_rate", {}).get("50pct", 0.0),
        completion=min(1.0, watch_time / (views * video_duration)) if views > 0 else 0.0,
        save_rate=(raw_data.get("saves", 0) / max(views, 1)) * 1000,
        share_velocity=(raw_data.get("shares", 0) / max(views, 1)) * 1000,
        comment_velocity=(raw_data.get("comments", 0) / max(views, 1)) * 1000,
        view_velocity=raw_data.get("views_first_30min", 0) / 30.0
    )

def map_instagram_signal(raw_data: Dict) -> NormalizedSignal:
    """
    Map Instagram API response to normalized signal
    
    Args:
        raw_data: Raw Instagram analytics
        
    Returns:
        NormalizedSignal
    """
    impressions = raw_data.get("impressions", 1)
    reach = raw_data.get("reach", 1)
    video_views = raw_data.get("video_views", 0)
    
    return NormalizedSignal(
        stop_rate=raw_data.get("retention_3s", 0.0),
        early_hold=raw_data.get("retention_25pct", 0.0),
        mid_hold=raw_data.get("retention_50pct", 0.0),
        completion=raw_data.get("completion_rate", 0.0),
        save_rate=(raw_data.get("saves", 0) / max(impressions, 1)) * 1000,
        share_velocity=(raw_data.get("shares", 0) / max(reach, 1)) * 1000,
        comment_velocity=(raw_data.get("comments", 0) / max(impressions, 1)) * 1000,
        view_velocity=(video_views / max(impressions, 1)) * 100.0  # Normalize
    )

def map_youtube_signal(raw_data: Dict) -> NormalizedSignal:
    """
    Map YouTube API response to normalized signal
    
    Args:
        raw_data: Raw YouTube analytics
        
    Returns:
        NormalizedSignal
    """
    views = raw_data.get("views", 1)
    
    # YouTube provides retention curve
    retention_curve = raw_data.get("retention_curve", [])
    
    stop_rate = retention_curve[0] if retention_curve else 0.0
    early_hold = retention_curve[len(retention_curve) // 4] if len(retention_curve) > 0 else 0.0
    mid_hold = retention_curve[len(retention_curve) // 2] if len(retention_curve) > 0 else 0.0
    
    return NormalizedSignal(
        stop_rate=stop_rate,
        early_hold=early_hold,
        mid_hold=mid_hold,
        completion=raw_data.get("average_view_duration", 0) / raw_data.get("video_duration", 1),
        save_rate=(raw_data.get("likes", 0) / max(views, 1)) * 1000,  # YouTube uses likes
        share_velocity=(raw_data.get("shares", 0) / max(views, 1)) * 1000,
        comment_velocity=(raw_data.get("comments", 0) / max(views, 1)) * 1000,
        view_velocity=raw_data.get("views_first_30min", 0) / 30.0
    )

def normalize_platform_signal(platform: str, raw_data: Dict) -> NormalizedSignal:
    """
    Normalize platform signal based on platform type
    
    Args:
        platform: Platform name (tiktok, instagram, youtube)
        raw_data: Raw platform analytics
        
    Returns:
        NormalizedSignal
    """
    platform = platform.lower()
    
    if platform == "tiktok":
        return map_tiktok_signal(raw_data)
    elif platform == "instagram":
        return map_instagram_signal(raw_data)
    elif platform == "youtube":
        return map_youtube_signal(raw_data)
    else:
        logger.warning(f"Unknown platform: {platform}, using default mapping")
        return NormalizedSignal(
            stop_rate=0.0,
            early_hold=0.0,
            mid_hold=0.0,
            completion=0.0,
            save_rate=0.0,
            share_velocity=0.0,
            comment_velocity=0.0,
            view_velocity=0.0
        )

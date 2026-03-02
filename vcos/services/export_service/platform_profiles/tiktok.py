"""
Export Service - TikTok Platform Profile
"""

PLATFORM_CONFIG = {
    "name": "tiktok",
    "aspect_ratio": "9:16",
    "resolution": (1080, 1920),
    "max_duration": 60,  # seconds
    "min_duration": 3,
    "max_file_size_mb": 287,
    "supported_formats": ["mp4"],
    "fps": 30,
    "bitrate": "5000k"
}

def get_export_settings():
    """Get TikTok export settings"""
    return PLATFORM_CONFIG

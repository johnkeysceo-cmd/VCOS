"""
Export Service - YouTube Shorts Platform Profile
"""

PLATFORM_CONFIG = {
    "name": "youtube_shorts",
    "aspect_ratio": "9:16",
    "resolution": (1080, 1920),
    "max_duration": 60,  # seconds
    "min_duration": 1,
    "max_file_size_mb": 256,
    "supported_formats": ["mp4"],
    "fps": 30,
    "bitrate": "8000k"
}

def get_export_settings():
    """Get YouTube Shorts export settings"""
    return PLATFORM_CONFIG

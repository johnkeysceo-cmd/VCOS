"""
Export Service - Instagram Platform Profile
"""

PLATFORM_CONFIG = {
    "name": "instagram",
    "aspect_ratio": "9:16",  # Reels
    "resolution": (1080, 1920),
    "max_duration": 90,  # seconds
    "min_duration": 3,
    "max_file_size_mb": 100,
    "supported_formats": ["mp4"],
    "fps": 30,
    "bitrate": "5000k"
}

def get_export_settings():
    """Get Instagram export settings"""
    return PLATFORM_CONFIG

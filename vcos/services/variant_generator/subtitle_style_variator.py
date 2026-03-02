"""
Variant Generator - Subtitle Style Variator
Varies subtitle styling (bold, colors, animations)
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Subtitle style presets
SUBTITLE_STYLES = {
    "bold": {
        "font_weight": "bold",
        "font_size": "large",
        "color": "#FFFFFF",
        "background": "#000000",
        "animation": "fade_in"
    },
    "minimal": {
        "font_weight": "normal",
        "font_size": "medium",
        "color": "#FFFFFF",
        "background": "transparent",
        "animation": "none"
    },
    "colorful": {
        "font_weight": "bold",
        "font_size": "large",
        "color": "#FF6B6B",
        "background": "#4ECDC4",
        "animation": "slide_in"
    },
    "outline": {
        "font_weight": "bold",
        "font_size": "large",
        "color": "#FFFFFF",
        "background": "transparent",
        "outline": "#000000",
        "animation": "pop"
    }
}

def style_subtitles(subtitles: List[Dict], theme: str = "bold") -> List[Dict]:
    """
    Apply styling to subtitles
    
    Args:
        subtitles: List of subtitle entries
        theme: Style theme name
        
    Returns:
        Styled subtitles
    """
    style_config = SUBTITLE_STYLES.get(theme, SUBTITLE_STYLES["bold"])
    
    styled = []
    for subtitle in subtitles:
        styled.append({
            **subtitle,
            "style": style_config
        })
    
    logger.info(f"Applied {theme} style to {len(styled)} subtitles")
    
    return styled

def generate_style_variants(subtitles: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Generate subtitles with all style variants
    
    Args:
        subtitles: Base subtitle list
        
    Returns:
        Dictionary mapping style names to styled subtitles
    """
    variants = {}
    
    for style_name in SUBTITLE_STYLES.keys():
        variants[style_name] = style_subtitles(subtitles, style_name)
    
    return variants

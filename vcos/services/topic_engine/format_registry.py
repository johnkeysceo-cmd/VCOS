"""
Topic Engine - Format Registry
Maintains format templates for different clusters
"""

# Format templates by cluster
CLUSTER_FORMATS = {
    "rebuild_tools": [
        "I rebuilt {target} in {timeframe}",
        "This replaces {target}",
        "{target} is outdated. Here's why.",
        "I built a better {target} in {timeframe}",
        "Why I stopped using {target}"
    ],
    "automation": [
        "I automated {target} in {timeframe}",
        "This script replaces {target} hours of work",
        "How I automated my entire {target} workflow",
        "{target} automation that saves {timeframe} hours/week"
    ],
    "ai_tools": [
        "This AI tool replaced {target}",
        "I tested {count} AI tools for {target}",
        "Why this AI tool is better than {target}",
        "This AI does {target} {multiplier}x faster"
    ],
    "replacement": [
        "This replaces {target}",
        "Why {target} isn't enough",
        "I switched from {target} to {replacement}",
        "{target} vs {replacement}: The truth"
    ],
    "challenge": [
        "I rebuilt {target} in {timeframe}",
        "Can I build {target} in {timeframe}?",
        "Building {target} from scratch",
        "I challenged myself to rebuild {target}"
    ],
    "tutorial": [
        "How to build {target}",
        "Building {target} step by step",
        "Complete guide to {target}",
        "Learn {target} in {timeframe}"
    ]
}

def get_formats_for_cluster(cluster: str) -> list:
    """
    Get format templates for a cluster
    
    Args:
        cluster: Cluster name
        
    Returns:
        List of format templates
    """
    return CLUSTER_FORMATS.get(cluster, CLUSTER_FORMATS["tutorial"])

def register_format(cluster: str, format_template: str):
    """Register a new format template for a cluster"""
    if cluster not in CLUSTER_FORMATS:
        CLUSTER_FORMATS[cluster] = []
    
    if format_template not in CLUSTER_FORMATS[cluster]:
        CLUSTER_FORMATS[cluster].append(format_template)

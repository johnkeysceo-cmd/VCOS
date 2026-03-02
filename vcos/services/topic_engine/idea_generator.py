"""
Topic Engine - Idea Generator
Generates new content ideas based on cluster performance
"""

from services.topic_engine.cluster_manager import get_top_cluster
from services.topic_engine.format_registry import get_formats_for_cluster
from services.topic_engine.trend_data_integration import trend_aggregator
from services.topic_engine.cultural_timing_analyzer import analyze_cultural_timing
from services.topic_engine.meme_dynamics_tracker import meme_dynamics_tracker
import logging

logger = logging.getLogger(__name__)

def generate_ideas(count: int = 5) -> list:
    """
    Generate new content ideas based on top performing cluster + trend data
    
    Args:
        count: Number of ideas to generate
        
    Returns:
        List of topic ideas with trend scores
    """
    cluster = get_top_cluster()
    formats = get_formats_for_cluster(cluster)
    
    # Get trending topics
    trending_topics = trend_aggregator.get_aggregated_trends()
    
    ideas = []
    
    # Generate ideas based on cluster and formats
    for i in range(count):
        if cluster == "rebuild_tools":
            base_ideas = [
                "I rebuilt X in 24 hours",
                "This might replace X",
                "X is outdated. Here's why.",
                "I built a better X in 72 hours",
                "Why I stopped using X"
            ]
        elif cluster == "automation":
            base_ideas = [
                "I automated X in 5 minutes",
                "This script replaces X hours of work",
                "How I automated my entire workflow",
                "X automation that saves 10 hours/week"
            ]
        elif cluster == "ai_tools":
            base_ideas = [
                "This AI tool replaced X",
                "I tested 10 AI tools for X",
                "Why this AI tool is better than X",
                "This AI does X 10x faster"
            ]
        else:
            base_ideas = [f"Topic idea {i+1} for {cluster}"]
        
        # Enhance with trending topics if available
        if trending_topics and i < len(trending_topics):
            trend_topic = trending_topics[i]["topic"]
            # Merge trend topic with base idea
            enhanced_idea = base_ideas[i % len(base_ideas)].replace("X", trend_topic)
            
            # Analyze meme dynamics
            meme_analysis = meme_dynamics_tracker.analyze_meme_lifecycle(enhanced_idea, cluster)
            
            ideas.append({
                "idea": enhanced_idea,
                "cluster": cluster,
                "trend_momentum": trending_topics[i]["momentum"],
                "meme_phase": meme_analysis["phase"],
                "opportunity_score": meme_analysis["opportunity_score"],
                "base_idea": base_ideas[i % len(base_ideas)]
            })
        else:
            base_idea = base_ideas[i % len(base_ideas)]
            meme_analysis = meme_dynamics_tracker.analyze_meme_lifecycle(base_idea, cluster)
            
            ideas.append({
                "idea": base_idea,
                "cluster": cluster,
                "trend_momentum": 0.5,
                "meme_phase": meme_analysis["phase"],
                "opportunity_score": meme_analysis["opportunity_score"],
                "base_idea": base_idea
            })
    
    # Sort by trend momentum
    ideas.sort(key=lambda x: x["trend_momentum"], reverse=True)
    
    # Return top N
    unique_ideas = ideas[:count]
    
    logger.info(f"Generated {len(unique_ideas)} ideas for cluster: {cluster} (with trend data)")
    
    # Return just the idea strings for backward compatibility
    # In production, could return full dicts with metadata
    return [idea["idea"] if isinstance(idea, dict) else idea for idea in unique_ideas]

async def generate_ideas_async(count: int = 5) -> list:
    """Async version of generate_ideas"""
    return generate_ideas(count)

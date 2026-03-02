"""
Prioritization Engine - Topic Recommender
Recommends next topics to create
"""

from services.prioritization_engine.cluster_scoring import score_clusters
from services.prioritization_engine.momentum_predictor import predict_momentum
from services.topic_engine.idea_generator import generate_ideas
import logging

logger = logging.getLogger(__name__)

async def recommend_next(count: int = 10) -> list:
    """
    Recommend next topics to create
    
    Args:
        count: Number of recommendations
        
    Returns:
        List of recommended topics with scores
    """
    # Get cluster scores
    cluster_scores = score_clusters()
    
    # Sort by score
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)
    
    recommendations = []
    
    for cluster, score in sorted_clusters[:3]:  # Top 3 clusters
        momentum = predict_momentum(cluster)
        
        # Generate ideas for this cluster
        ideas = generate_ideas(count=3)
        
        for idea in ideas:
            recommendations.append({
                "topic": idea,
                "cluster": cluster,
                "cluster_score": score,
                "momentum": momentum,
                "priority_score": score * 0.7 + momentum * 0.3
            })
    
    # Sort by priority score
    recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
    
    logger.info(f"Generated {len(recommendations)} topic recommendations")
    
    return recommendations[:count]

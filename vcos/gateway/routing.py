"""
VCOS Gateway - Request routing
Routes external requests to internal services
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from gateway.auth import validate_api_key
from orchestration.pipeline_manager import start_batch_pipeline
from shared.schemas.batch_schema import BatchRequest, BatchResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["vcos"])

@router.post("/batch", response_model=BatchResponse)
async def create_batch(
    payload: BatchRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Create a new content batch
    Triggers the full pipeline: idea generation -> hook creation -> recording -> optimization -> variants
    """
    try:
        # Validate API key
        if x_api_key:
            validate_api_key(x_api_key)
        
        # Start the batch pipeline
        job_id = await start_batch_pipeline(payload.dict())
        
        logger.info(f"Batch job created: {job_id}")
        
        return BatchResponse(
            job_id=job_id,
            status="queued",
            message="Batch pipeline started successfully"
        )
    except Exception as e:
        logger.error(f"Error creating batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch/{job_id}")
async def get_batch_status(job_id: str):
    """Get status of a batch job"""
    from orchestration.pipeline_manager import get_job_status
    
    try:
        status = await get_job_status(job_id)
        return status
    except Exception as e:
        logger.error(f"Error getting batch status: {e}")
        return {"job_id": job_id, "status": "unknown", "error": str(e)}

@router.post("/hook/generate")
async def generate_hooks(
    topic: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Generate hooks for a given topic"""
    if x_api_key:
        validate_api_key(x_api_key)
    
    # Import here to avoid circular dependencies
    from services.hook_engine.hook_scorer import generate_hooks_for_topic
    
    hooks = await generate_hooks_for_topic(topic)
    return {"hooks": hooks}

@router.post("/topic/suggest")
async def suggest_topics(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Get topic suggestions based on cluster performance"""
    if x_api_key:
        validate_api_key(x_api_key)
    
    from services.prioritization_engine.topic_recommender import recommend_next
    
    recommendations = await recommend_next()
    return {"recommendations": recommendations}

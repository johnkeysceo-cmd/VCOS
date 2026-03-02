"""
Orchestration - Batch Runner
Runs batch jobs
"""

import asyncio
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

async def run_batch(jobs: List[Dict], max_concurrent: int = 3):
    """
    Run multiple jobs in batch
    
    Args:
        jobs: List of job configurations
        max_concurrent: Maximum concurrent jobs
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_job(job):
        async with semaphore:
            from orchestration.pipeline_manager import run_pipeline
            await run_pipeline(job["job_id"], job["payload"])
    
    await asyncio.gather(*[run_job(job) for job in jobs])
    logger.info(f"Batch completed: {len(jobs)} jobs")

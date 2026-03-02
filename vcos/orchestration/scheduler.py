"""
Orchestration - Scheduler
Schedules batch jobs and periodic tasks
"""

import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    """Simple task scheduler"""
    
    def __init__(self):
        self.tasks = []
    
    async def schedule_periodic(self, func, interval_seconds: float):
        """Schedule a periodic task"""
        while True:
            await func()
            await asyncio.sleep(interval_seconds)
    
    async def schedule_delayed(self, func, delay_seconds: float):
        """Schedule a delayed task"""
        await asyncio.sleep(delay_seconds)
        await func()

scheduler = Scheduler()

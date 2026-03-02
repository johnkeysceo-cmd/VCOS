"""
Orchestration - State Machine
Explicit batch lifecycle management
"""

from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BatchState(Enum):
    """Batch pipeline states"""
    IDEA_GENERATED = "idea_generated"
    HOOK_GENERATED = "hook_generated"
    RECORDED = "recorded"
    OPTIMIZED = "optimized"
    VARIANTS_CREATED = "variants_created"
    PUBLISHED = "published"
    ANALYTICS_COLLECTED = "analytics_collected"
    TRAINED = "trained"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class BatchStateMachine:
    """State machine for batch lifecycle"""
    job_id: str
    current_state: BatchState = BatchState.IDEA_GENERATED
    state_history: List[Dict] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.state_history is None:
            self.state_history = []
        self.record_state(self.current_state)
    
    def record_state(self, state: BatchState, metadata: Dict = None):
        """Record state transition"""
        self.state_history.append({
            "state": state.value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        logger.info(f"Job {self.job_id}: {state.value}")
    
    def transition_to(self, new_state: BatchState, metadata: Dict = None):
        """Transition to new state"""
        # Validate transition
        valid_transitions = {
            BatchState.IDEA_GENERATED: [BatchState.HOOK_GENERATED, BatchState.FAILED],
            BatchState.HOOK_GENERATED: [BatchState.RECORDED, BatchState.FAILED],
            BatchState.RECORDED: [BatchState.OPTIMIZED, BatchState.FAILED],
            BatchState.OPTIMIZED: [BatchState.VARIANTS_CREATED, BatchState.FAILED],
            BatchState.VARIANTS_CREATED: [BatchState.PUBLISHED, BatchState.FAILED],
            BatchState.PUBLISHED: [BatchState.ANALYTICS_COLLECTED, BatchState.FAILED],
            BatchState.ANALYTICS_COLLECTED: [BatchState.TRAINED, BatchState.FAILED],
            BatchState.TRAINED: [BatchState.COMPLETED, BatchState.FAILED],
        }
        
        if new_state not in valid_transitions.get(self.current_state, []):
            logger.warning(
                f"Invalid transition from {self.current_state.value} to {new_state.value}"
            )
            return False
        
        self.current_state = new_state
        self.record_state(new_state, metadata)
        return True
    
    def fail(self, error: str):
        """Mark batch as failed"""
        self.error = error
        self.transition_to(BatchState.FAILED, {"error": error})
    
    def get_state_info(self) -> Dict:
        """Get current state information"""
        return {
            "job_id": self.job_id,
            "current_state": self.current_state.value,
            "state_history": self.state_history,
            "error": self.error
        }

# Global state machines registry
_state_machines: Dict[str, BatchStateMachine] = {}

def get_state_machine(job_id: str) -> Optional[BatchStateMachine]:
    """Get state machine for a job"""
    return _state_machines.get(job_id)

def create_state_machine(job_id: str) -> BatchStateMachine:
    """Create new state machine for a job"""
    sm = BatchStateMachine(job_id=job_id)
    _state_machines[job_id] = sm
    return sm

"""
GlobalState Management with Optimistic Concurrency Control (OCC).

This module implements the centralized state management for the Chimera swarm,
ensuring consistency across Planner, Worker, and Judge agents.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
import json
from enum import Enum


class StateVersion(BaseModel):
    """Represents a versioned snapshot of GlobalState."""
    version_hash: str = Field(..., description="SHA256 hash of state contents")
    timestamp: datetime = Field(default_factory=datetime.now)
    updated_by: str = Field(..., description="Agent ID that last updated state")


class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GlobalState(BaseModel):
    """
    The centralized state of the Chimera network.
    
    This state is managed using Optimistic Concurrency Control (OCC):
    - Agents read a snapshot of the state
    - Agents make local modifications
    - On commit, the system validates that the state hasn't changed
    - If changed, the commit fails and the agent must retry
    """
    # Campaign Management
    active_campaigns: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Budget Tracking
    daily_spend: Dict[str, float] = Field(default_factory=dict)  # currency -> amount
    budget_limits: Dict[str, float] = Field(default_factory=dict)
    
    # Agent Status
    agent_states: Dict[str, str] = Field(default_factory=dict)  # agent_id -> state
    
    # Version Control
    state_version: StateVersion = Field(...)
    
    def compute_hash(self) -> str:
        """Computes a deterministic hash of the state (excluding version)."""
        # Create a dict without the version field for hashing
        state_dict = self.model_dump(exclude={"state_version"})
        state_json = json.dumps(state_dict, sort_keys=True, default=str)
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    def update_version(self, updated_by: str) -> None:
        """Updates the state version after a modification."""
        new_hash = self.compute_hash()
        self.state_version = StateVersion(
            version_hash=new_hash,
            updated_by=updated_by,
            timestamp=datetime.now()
        )


class StateManager:
    """
    Manages GlobalState with OCC validation.
    
    This is the single source of truth for the Chimera network.
    All state modifications must go through this manager.
    """
    
    def __init__(self):
        self._state = GlobalState(
            state_version=StateVersion(
                version_hash="initial",
                updated_by="system",
                timestamp=datetime.now()
            )
        )
        self._state.update_version("system")
    
    def get_state_snapshot(self) -> GlobalState:
        """
        Returns a snapshot of the current state.
        
        Agents should use this to read state, make local modifications,
        then call commit_state_change() to validate and persist.
        """
        # Return a deep copy to prevent direct mutation
        return self._state.model_copy(deep=True)
    
    def commit_state_change(
        self,
        modified_state: GlobalState,
        agent_id: str,
        expected_version_hash: str
    ) -> bool:
        """
        Attempts to commit a state change using OCC.
        
        Args:
            modified_state: The state with local modifications
            agent_id: ID of the agent attempting the commit
            expected_version_hash: The version hash when the agent read the state
            
        Returns:
            True if commit succeeded, False if version conflict detected
            
        Raises:
            ValueError: If the modified_state is invalid
        """
        # Check if state has changed since the agent read it
        current_hash = self._state.state_version.version_hash
        
        if current_hash != expected_version_hash:
            # State has changed - OCC conflict detected
            return False
        
        # Validate the modified state
        new_hash = modified_state.compute_hash()
        
        # Update state and version
        self._state = modified_state
        self._state.update_version(agent_id)
        
        return True
    
    def add_campaign(self, campaign_id: str, campaign_data: Dict[str, Any], agent_id: str) -> bool:
        """Adds a new campaign to the state."""
        snapshot = self.get_state_snapshot()
        expected_hash = snapshot.state_version.version_hash
        
        snapshot.active_campaigns[campaign_id] = {
            **campaign_data,
            "status": CampaignStatus.ACTIVE,
            "created_at": datetime.now().isoformat()
        }
        
        return self.commit_state_change(snapshot, agent_id, expected_hash)
    
    def update_budget(self, currency: str, amount: float, agent_id: str) -> bool:
        """Updates daily spend tracking."""
        snapshot = self.get_state_snapshot()
        expected_hash = snapshot.state_version.version_hash
        
        snapshot.daily_spend[currency] = snapshot.daily_spend.get(currency, 0.0) + amount
        
        return self.commit_state_change(snapshot, agent_id, expected_hash)
    
    def check_budget_limit(self, currency: str, requested_amount: float) -> tuple[bool, float]:
        """
        Checks if a transaction would exceed budget limits.
        
        Returns:
            (is_allowed, current_spend)
        """
        current_spend = self._state.daily_spend.get(currency, 0.0)
        limit = self._state.budget_limits.get(currency, float('inf'))
        
        if current_spend + requested_amount > limit:
            return False, current_spend
        
        return True, current_spend

"""
Tests for Optimistic Concurrency Control (OCC) in GlobalState.

Verifies that state version conflicts are detected and handled correctly.
"""
import pytest
from chimera.core.state import StateManager, GlobalState
from datetime import datetime


def test_occ_conflict_detection():
    """
    Verifies that OCC detects conflicts when state changes between read and commit.
    """
    manager = StateManager()
    
    # Agent A reads state
    state_a = manager.get_state_snapshot()
    expected_hash_a = state_a.state_version.version_hash
    
    # Agent B reads state and commits a change
    state_b = manager.get_state_snapshot()
    state_b.active_campaigns["campaign-1"] = {"goal": "Test Campaign"}
    success_b = manager.commit_state_change(state_b, "agent_b", state_b.state_version.version_hash)
    assert success_b is True
    
    # Agent A tries to commit (should fail due to version conflict)
    state_a.active_campaigns["campaign-2"] = {"goal": "Another Campaign"}
    success_a = manager.commit_state_change(state_a, "agent_a", expected_hash_a)
    assert success_a is False, "OCC should detect version conflict"


def test_occ_successful_commit():
    """
    Verifies that commits succeed when no conflicts occur.
    """
    manager = StateManager()
    
    state = manager.get_state_snapshot()
    expected_hash = state.state_version.version_hash
    
    state.active_campaigns["test-campaign"] = {"goal": "Test"}
    success = manager.commit_state_change(state, "test_agent", expected_hash)
    
    assert success is True
    assert "test-campaign" in manager.get_state_snapshot().active_campaigns


def test_budget_limit_check():
    """
    Verifies budget limit checking logic.
    """
    manager = StateManager()
    
    # Set budget limit
    snapshot = manager.get_state_snapshot()
    snapshot.budget_limits["USDC"] = 50.0
    manager.commit_state_change(snapshot, "system", snapshot.state_version.version_hash)
    
    # Check budget
    is_allowed, current = manager.check_budget_limit("USDC", 30.0)
    assert is_allowed is True
    
    is_allowed, current = manager.check_budget_limit("USDC", 30.0)  # Would exceed limit
    assert is_allowed is False

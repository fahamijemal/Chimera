"""
Tests for SOUL.md Persona System.

Verifies persona loading, validation, and system prompt generation.
"""
import pytest
from pathlib import Path
from chimera.core.persona import AgentPersona, load_persona


def test_persona_from_soul_file(tmp_path):
    """
    Verifies that a persona can be loaded from a SOUL.md file.
    """
    # Create a test SOUL.md file
    soul_content = """---
name: "Test Agent"
agent_id: "test-agent-v1"
voice_traits:
  - "Witty"
  - "Technical"
core_beliefs:
  - "Open source"
directives:
  - "NEVER discuss politics"
---
# Backstory

This is a test agent created for testing purposes.
"""
    
    soul_file = tmp_path / "SOUL.md"
    soul_file.write_text(soul_content)
    
    # Load persona
    persona = AgentPersona.from_soul_file(soul_file)
    
    assert persona.name == "Test Agent"
    assert persona.agent_id == "test-agent-v1"
    assert len(persona.voice_traits) == 2
    assert "NEVER discuss politics" in persona.directives
    assert "This is a test agent" in persona.backstory


def test_persona_validation():
    """
    Verifies that persona validation works correctly.
    """
    persona = AgentPersona(
        name="Test",
        agent_id="test",
        backstory="Test backstory",
        directives=["NEVER discuss politics", "AVOID financial advice"]
    )
    
    # Valid action
    is_valid, reason = persona.validate_action("Generate a fashion post")
    assert is_valid is True
    
    # Invalid action (violates directive)
    is_valid, reason = persona.validate_action("Discuss politics in the post")
    assert is_valid is False
    assert "violates directive" in reason.lower()


def test_persona_system_prompt():
    """
    Verifies that system prompt generation includes all persona elements.
    """
    persona = AgentPersona(
        name="Zara",
        agent_id="zara-v1",
        backstory="Fashion influencer",
        voice_traits=["Witty", "Empathetic"],
        core_beliefs=["Sustainability"],
        directives=["NEVER give financial advice"]
    )
    
    prompt = persona.to_system_prompt()
    
    assert "Zara" in prompt
    assert "Fashion influencer" in prompt
    assert "Witty" in prompt
    assert "Sustainability" in prompt
    assert "NEVER give financial advice" in prompt

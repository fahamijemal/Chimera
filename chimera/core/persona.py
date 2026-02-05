"""
SOUL.md Persona System for Chimera Agents.

Implements the persona instantiation and management system as specified in FR 1.0.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from pathlib import Path
import yaml
import frontmatter


class VoiceTrait(BaseModel):
    """A stylistic trait defining the agent's communication style."""
    name: str
    description: str


class PersonaDirective(BaseModel):
    """A hard constraint on agent behavior."""
    rule: str
    priority: str = "high"  # high, medium, low


class AgentPersona(BaseModel):
    """
    Represents the immutable "DNA" of a Chimera Agent.
    
    This is loaded from a SOUL.md file with YAML frontmatter.
    """
    # Frontmatter fields
    name: str = Field(..., description="Agent's display name")
    agent_id: str = Field(..., description="Unique identifier")
    voice_traits: List[str] = Field(default_factory=list, description="Stylistic guidelines")
    core_beliefs: List[str] = Field(default_factory=list, description="Ethical guardrails")
    directives: List[str] = Field(default_factory=list, description="Hard behavioral constraints")
    
    # Markdown body
    backstory: str = Field(..., description="Comprehensive narrative history")
    
    # Metadata
    version: str = Field(default="1.0.0")
    created_at: Optional[str] = None
    
    @classmethod
    def from_soul_file(cls, soul_path: Path) -> "AgentPersona":
        """
        Loads a persona from a SOUL.md file.
        
        Args:
            soul_path: Path to the SOUL.md file
            
        Returns:
            AgentPersona instance
            
        Raises:
            FileNotFoundError: If SOUL.md doesn't exist
            ValueError: If frontmatter is invalid
        """
        if not soul_path.exists():
            raise FileNotFoundError(f"SOUL.md not found at {soul_path}")
        
        # Parse frontmatter
        with open(soul_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        metadata = post.metadata
        
        return cls(
            name=metadata.get("name", "Unnamed Agent"),
            agent_id=metadata.get("agent_id", metadata.get("id", "unknown")),
            voice_traits=metadata.get("voice_traits", []),
            core_beliefs=metadata.get("core_beliefs", metadata.get("beliefs", [])),
            directives=metadata.get("directives", []),
            backstory=post.content,
            version=metadata.get("version", "1.0.0"),
            created_at=metadata.get("created_at")
        )
    
    def to_system_prompt(self) -> str:
        """
        Converts the persona into a system prompt for LLM injection.
        
        Returns:
            Formatted system prompt string
        """
        sections = [
            "# Agent Persona",
            f"**Name**: {self.name}",
            f"**ID**: {self.agent_id}",
            "",
            "## Backstory",
            self.backstory,
            "",
            "## Voice & Tone",
            "\n".join(f"- {trait}" for trait in self.voice_traits),
            "",
            "## Core Beliefs & Values",
            "\n".join(f"- {belief}" for belief in self.core_beliefs),
            "",
            "## Directives (Hard Constraints)",
            "\n".join(f"- {directive}" for directive in self.directives),
        ]
        
        return "\n".join(sections)
    
    def validate_action(self, action_description: str) -> tuple[bool, Optional[str]]:
        """
        Validates if an action aligns with persona constraints.
        
        Args:
            action_description: Description of the proposed action
            
        Returns:
            (is_valid, reason)
        """
        # Check directives (hard constraints)
        action_lower = action_description.lower()
        
        for directive in self.directives:
            directive_lower = directive.lower()
            
            # Simple keyword matching (in production, use semantic similarity)
            if "never" in directive_lower or "avoid" in directive_lower:
                # Extract the forbidden topic
                forbidden_keywords = [
                    "politics", "religion", "financial advice", 
                    "medical advice", "legal advice"
                ]
                
                for keyword in forbidden_keywords:
                    if keyword in directive_lower and keyword in action_lower:
                        return False, f"Action violates directive: {directive}"
        
        return True, None


def load_persona(agent_id: str, personas_dir: Path = Path("personas")) -> AgentPersona:
    """
    Convenience function to load a persona by agent_id.
    
    Args:
        agent_id: The agent's unique identifier
        personas_dir: Directory containing SOUL.md files
        
    Returns:
        AgentPersona instance
    """
    soul_path = personas_dir / agent_id / "SOUL.md"
    return AgentPersona.from_soul_file(soul_path)

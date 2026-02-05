"""
MCP Server for Weaviate Memory Integration.

Exposes memory operations as MCP Tools and Resources for the Chimera agents.
"""
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import os
from chimera.core.memory import MemoryManager

# Create FastMCP server
mcp = FastMCP("chimera-weaviate")

# Initialize memory manager (lazy initialization)
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Gets or creates the memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(
            weaviate_url=os.getenv("WEAVIATE_URL", "http://localhost:8080"),
            api_key=os.getenv("WEAVIATE_API_KEY")
        )
    return _memory_manager


@mcp.resource("memory://agent/{agent_id}/recent")
def get_recent_memories(agent_id: str) -> str:
    """
    Resource: Returns recent memories for an agent.
    
    Args:
        agent_id: Agent identifier
    """
    manager = get_memory_manager()
    memories = manager.search_memories(
        query="recent interactions",
        agent_id=agent_id,
        limit=10,
        memory_type="episodic"
    )
    
    return "\n".join([f"- {m.content[:100]}..." for m in memories])


@mcp.tool()
def search_memory(
    agent_id: str,
    query: str,
    limit: int = 5,
    memory_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Tool: Searches agent memories using semantic search.
    
    Args:
        agent_id: Agent identifier
        query: Search query
        limit: Maximum results
        memory_type: Filter by type (optional)
    """
    manager = get_memory_manager()
    memories = manager.search_memories(
        query=query,
        agent_id=agent_id,
        limit=limit,
        memory_type=memory_type
    )
    
    return [
        {
            "content": m.content,
            "timestamp": m.timestamp.isoformat(),
            "importance_score": m.importance_score,
            "memory_type": m.memory_type
        }
        for m in memories
    ]


@mcp.tool()
def store_memory(
    agent_id: str,
    content: str,
    memory_type: str = "episodic",
    importance_score: float = 0.5
) -> Dict[str, Any]:
    """
    Tool: Stores a new memory.
    
    Args:
        agent_id: Agent identifier
        content: Memory content
        memory_type: Type of memory
        importance_score: Importance (0.0 to 1.0)
    """
    manager = get_memory_manager()
    memory_id = manager.store_memory(
        content=content,
        agent_id=agent_id,
        memory_type=memory_type,
        importance_score=importance_score
    )
    
    return {
        "status": "success",
        "memory_id": memory_id,
        "agent_id": agent_id
    }


@mcp.tool()
def assemble_context(agent_id: str, input_query: str) -> str:
    """
    Tool: Assembles context for LLM injection.
    
    Args:
        agent_id: Agent identifier
        input_query: Current input query
    """
    manager = get_memory_manager()
    return manager.assemble_context(agent_id, input_query)


if __name__ == "__main__":
    mcp.run()

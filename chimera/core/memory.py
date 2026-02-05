"""
Weaviate Memory Integration for Hierarchical Memory Retrieval.

Implements FR 1.1: Hierarchical Memory Retrieval using RAG pipeline.
"""
from typing import List, Dict, Any, Optional
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from datetime import datetime
import os
from pydantic import BaseModel


class Memory(BaseModel):
    """Represents a single memory entry in Weaviate."""
    content: str
    agent_id: str
    timestamp: datetime
    importance_score: float = 0.5
    memory_type: str = "episodic"  # episodic, semantic, biographical
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryManager:
    """
    Manages agent memories using Weaviate vector database.
    
    Implements the RAG pipeline for long-term semantic memory retrieval.
    """
    
    def __init__(self, weaviate_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Weaviate client.
        
        Args:
            weaviate_url: Weaviate instance URL (defaults to WEAVIATE_URL env var)
            api_key: API key for authentication (defaults to WEAVIATE_API_KEY env var)
        """
        self.weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = api_key or os.getenv("WEAVIATE_API_KEY")
        
        # Initialize client (using v4 API)
        # Initialize client (using v4 API)
        try:
            from weaviate.classes.init import Auth
            
            connect_kwargs = {
                "url": self.weaviate_url,
            }
            
            if self.api_key:
                connect_kwargs["auth_credentials"] = Auth.api_key(self.api_key)
                
            self.client = weaviate.WeaviateClient(**connect_kwargs)
            self.client.connect() # Explicitly open connection for v4
            
            if not self.client.is_live():
                 logger.warning(f"Weaviate at {self.weaviate_url} is not live.")
                 self.client = None

        except Exception as e:
            logger.warning(f"Failed to initialize Weaviate client: {e}. Using mock mode.")
            self.client = None
        
        # Ensure collection exists
        if self.client:
            self._ensure_collection()
    
    def _ensure_collection(self):
        """Creates the Memory collection if it doesn't exist."""
        if not self.client:
            return
        
        collection_name = "AgentMemory"
        
        try:
            # Check if collection exists
            if not self.client.collections.exists(collection_name):
                self.client.collections.create(
                    name=collection_name,
                    properties=[
                        Property(name="content", data_type=DataType.TEXT),
                        Property(name="agent_id", data_type=DataType.TEXT),
                        Property(name="timestamp", data_type=DataType.DATE),
                        Property(name="importance_score", data_type=DataType.NUMBER),
                        Property(name="memory_type", data_type=DataType.TEXT),
                    ],
                    vectorizer_config=Configure.Vectorizer.text2vec_openai(),  # or use other vectorizers
                )
        except Exception as e:
            logger.warning(f"Failed to ensure collection exists: {e}")
    
    def store_memory(
        self,
        content: str,
        agent_id: str,
        memory_type: str = "episodic",
        importance_score: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Stores a memory in Weaviate.
        
        Args:
            content: The memory content (will be vectorized)
            agent_id: ID of the agent this memory belongs to
            memory_type: Type of memory (episodic, semantic, biographical)
            importance_score: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            Memory UUID
        """
        if not self.client:
            logger.warning("Weaviate client not available. Memory not stored.")
            return "mock-uuid"
        
        try:
            collection = self.client.collections.get("AgentMemory")
            
            memory_obj = {
                "content": content,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "importance_score": importance_score,
                "memory_type": memory_type,
                **{f"metadata_{k}": v for k, v in (metadata or {}).items()}
            }
            
            result = collection.data.insert(memory_obj)
            return str(result)
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return "error-uuid"
    
    def search_memories(
        self,
        query: str,
        agent_id: str,
        limit: int = 5,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0
    ) -> List[Memory]:
        """
        Searches for semantically relevant memories using RAG.
        
        Args:
            query: Search query (will be vectorized and matched)
            agent_id: Filter memories by agent ID
            limit: Maximum number of results
            memory_type: Filter by memory type (optional)
            min_importance: Minimum importance score threshold
            
        Returns:
            List of relevant Memory objects
        """
        if not self.client:
            logger.warning("Weaviate client not available. Returning empty results.")
            return []
        
        try:
            collection = self.client.collections.get("AgentMemory")
            
            # Build query with filters
            from weaviate.classes.query import Filter
            where_filter = Filter.by_property("agent_id").equal(agent_id)
            
            if memory_type:
                where_filter = Filter.all_of([
                    Filter.by_property("agent_id").equal(agent_id),
                    Filter.by_property("memory_type").equal(memory_type)
                ])
            
            # Perform semantic search
            result = collection.query.near_text(
                query=query,
                limit=limit,
                where=where_filter,
                return_metadata=["distance", "certainty"]
            )
            
            memories = []
            for obj in result.objects:
                props = obj.properties
                # Filter by importance if needed
                importance = props.get("importance_score", 0.0)
                if importance >= min_importance:
                    memories.append(Memory(
                        content=props["content"],
                        agent_id=props["agent_id"],
                        timestamp=datetime.fromisoformat(props["timestamp"]),
                        importance_score=importance,
                        memory_type=props.get("memory_type", "episodic"),
                        metadata={k.replace("metadata_", ""): v for k, v in props.items() if k.startswith("metadata_")}
                    ))
            
            return memories
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def assemble_context(
        self,
        agent_id: str,
        input_query: str,
        short_term_memories: Optional[List[str]] = None
    ) -> str:
        """
        Assembles a complete context prompt combining:
        - Short-term memories (from Redis)
        - Long-term semantic memories (from Weaviate)
        
        Args:
            agent_id: Agent identifier
            input_query: Current input/query
            short_term_memories: Recent conversation history (last hour)
            
        Returns:
            Formatted context string for LLM injection
        """
        # Retrieve long-term memories
        long_term = self.search_memories(input_query, agent_id, limit=5)
        
        # Build context sections
        sections = [
            "# Context Assembly",
            "",
            "## Short-Term Memory (Last Hour)",
        ]
        
        if short_term_memories:
            for i, memory in enumerate(short_term_memories[-10:], 1):  # Last 10 items
                sections.append(f"{i}. {memory}")
        else:
            sections.append("(No recent memories)")
        
        sections.extend([
            "",
            "## Long-Term Semantic Memory (Relevant Past Interactions)",
        ])
        
        if long_term:
            for i, memory in enumerate(long_term, 1):
                sections.append(
                    f"{i}. [{memory.memory_type.upper()}] "
                    f"(Importance: {memory.importance_score:.2f}) "
                    f"{memory.content[:200]}..."
                )
        else:
            sections.append("(No relevant past memories found)")
        
        return "\n".join(sections)

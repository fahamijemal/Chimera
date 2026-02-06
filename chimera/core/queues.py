"""
Redis-based Queue Infrastructure for the Chimera Swarm.

Implements TaskQueue (Planner -> Worker) and ReviewQueue (Worker -> Judge).
"""
from typing import Optional
import json
try:
    import redis.asyncio as redis
except ImportError:
    # Fallback for older redis versions
    import redis
from chimera.core.models import Task, TaskResult
import os


class QueueManager:
    """
    Manages Redis queues for the FastRender Swarm pattern.
    
    Queues:
    - task_queue: Planner pushes tasks, Workers pop tasks
    - review_queue: Workers push results, Judges pop results
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize queue manager.
        
        Args:
            redis_url: Redis connection URL (defaults to REDIS_URL env var or localhost)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Establishes Redis connection."""
        # Parse URL to handle potential redactions or specific flags if needed
        # In most cases, redis.from_url handles user:pass@host:port/db correctly
        # We add SSL context handling if secure connection is implied
        try:
            connection_kwargs = {
                "decode_responses": True,
                "socket_connect_timeout": 5,
                "socket_keepalive": True,
                "health_check_interval": 30
            }
            
            # Check for SSL requirement (rediss:// scheme)
            if self.redis_url.startswith("rediss://"):
                 connection_kwargs["ssl_cert_reqs"] = None  # Or use proper cert logic if provided in env
            
            self._client = await redis.from_url(self.redis_url, **connection_kwargs)
        except Exception as e:
            # Fallback or re-raise with context
            print(f"Failed to connect to Redis: {e}")
            self._client = None

    
    async def disconnect(self):
        """Closes Redis connection."""
        if self._client:
            await self._client.aclose()
    
    # TaskQueue Operations (Planner -> Worker)
    
    async def push_task(self, task: Task) -> bool:
        """
        Pushes a task to the task_queue.
        
        Args:
            task: Task object to enqueue
            
        Returns:
            True if successful
        """
        if not self._client:
            await self.connect()
        
        task_json = task.model_dump_json()
        await self._client.lpush("task_queue", task_json)
        return True
    
    async def pop_task(self, timeout: int = 5) -> Optional[Task]:
        """
        Pops a task from the task_queue (blocking).
        
        Args:
            timeout: Blocking timeout in seconds
            
        Returns:
            Task object or None if timeout
        """
        if not self._client:
            await self.connect()
        
        result = await self._client.brpop("task_queue", timeout=timeout)
        
        if result is None:
            return None
        
        _, task_json = result
        task_dict = json.loads(task_json)
        return Task(**task_dict)
    
    async def get_task_count(self) -> int:
        """Returns the number of pending tasks."""
        if not self._client:
            await self.connect()
        
        return await self._client.llen("task_queue")
    
    # ReviewQueue Operations (Worker -> Judge)
    
    async def push_result(self, result: TaskResult) -> bool:
        """
        Pushes a result to the review_queue.
        
        Args:
            result: TaskResult object to enqueue
            
        Returns:
            True if successful
        """
        if not self._client:
            await self.connect()
        
        result_json = result.model_dump_json()
        await self._client.lpush("review_queue", result_json)
        return True
    
    async def pop_result(self, timeout: int = 5) -> Optional[TaskResult]:
        """
        Pops a result from the review_queue (blocking).
        
        Args:
            timeout: Blocking timeout in seconds
            
        Returns:
            TaskResult object or None if timeout
        """
        if not self._client:
            await self.connect()
        
        result = await self._client.brpop("review_queue", timeout=timeout)
        
        if result is None:
            return None
        
        _, result_json = result
        result_dict = json.loads(result_json)
        return TaskResult(**result_dict)
    
    async def get_review_count(self) -> int:
        """Returns the number of pending reviews."""
        if not self._client:
            await self.connect()
        
        return await self._client.llen("review_queue")

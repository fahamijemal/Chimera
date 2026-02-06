"""
Test script for Dynamic Worker Agent.
"""
import asyncio
import logging
import os
from chimera.agents.worker import WorkerAgent
from chimera.core.models import Task, TaskType, TaskContext, TaskPriority
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.ERROR)  # Reduce noise

async def test_dynamic_worker():
    print("Initializing Worker Agents...")
    
    # Path to servers
    base_path = os.path.abspath("chimera/mcp/servers")
    image_server = os.path.join(base_path, "image_server.py")
    social_server = os.path.join(base_path, "social_server.py")
    
    # Test Case 1: Image Generation
    print("\n--- Test Case 1: Image Generation (using image_server) ---")
    worker_image = WorkerAgent(server_script_path=image_server)
    
    task1 = Task(
        task_id="test-1",
        task_type=TaskType.GENERATE_CONTENT,
        priority=TaskPriority.HIGH,
        context=TaskContext(
            goal_description="Create a promotional image for a neon-lit coffee shop in Tokyo. Side view. Style: Cyberpunk.",
            persona_constraints=["High quality", "Futuristic"]
        )
    )
    
    result1 = await worker_image.execute_task(task1)
    print(f"Result 1 Status: {result1.status}")
    print(f"Result 1 Output: {result1.output}")
    
    # Test Case 2: Social Post
    print("\n--- Test Case 2: Social Post (using social_server) ---")
    worker_social = WorkerAgent(server_script_path=social_server)
    
    task2 = Task(
        task_id="test-2",
        task_type=TaskType.SOCIAL_ACTION,
        priority=TaskPriority.MEDIUM,
        context=TaskContext(
            goal_description="Post a tweet announcing the grand opening of the Chimera Cafe. Hashtag #ChimeraCafe",
            persona_constraints=["Platform: Twitter"]
        )
    )
    
    result2 = await worker_social.execute_task(task2)
    print(f"Result 2 Status: {result2.status}")
    print(f"Result 2 Output: {result2.output}")

if __name__ == "__main__":
    asyncio.run(test_dynamic_worker())

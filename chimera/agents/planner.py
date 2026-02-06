from typing import List
import logging
import asyncio
from pydantic import BaseModel
from chimera.core.models import Task, TaskType, TaskContext, TaskPriority
from chimera.core.llm import LLMClient

logger = logging.getLogger(__name__)

class TaskList(BaseModel):
    """Container for list of tasks to support structured output."""
    tasks: List[Task]

class PlannerAgent:
    """
    Planner Agent: Decomposes goals into tasks using LLM.
    """
    def __init__(self):
        self.llm = LLMClient()

    def decompose_goal(self, goal: str) -> List[Task]:
        """
        Takes a high-level goal and returns a list of Tasks using the LLM.
        Note: The LLM call is async, so we use asyncio.run/create_task if called synchronously,
        but for the prototype we will make a blocking wrapper or assume async context.
        To keep the interface compatible with existing code, we'll run the async call.
        """
        print(f"[Planner] Decomposing goal with LLM: {goal}")
        
        try:
            return asyncio.run(self._decompose_async(goal))
        except Exception as e:
            logger.error(f"Failed to decompose goal with LLM: {e}")
            # Fallback to empty list or basic task if LLM fails
            return []

    async def _decompose_async(self, goal: str) -> List[Task]:
        """Async implementation of decomposition."""
        
        system_prompt = """
        You are the Planner Agent for Project Chimera. 
        Your job is to break down a high-level marketing goal into concrete, executable Tasks for Worker Agents.
        
        Available Task Types:
        - generate_content: Create text/image/video. Context should include style/persona details.
        - social_action: Post/Reply/Like. Context should specify platform and content reference.
        - transaction: Execute financial transaction. Context should specify amount/recipient.
        
        Priorities: high, medium, low.
        """
        
        prompt = f"Goal: {goal}\n\nCreate a list of tasks to achieve this goal."
        
        try:
            result: TaskList = await self.llm.generate_structured(
                prompt=prompt,
                response_model=TaskList,
                system_instruction=system_prompt
            )
            return result.tasks
        except Exception as e:
            logger.error(f"LLM Structure Error: {e}")
            return []


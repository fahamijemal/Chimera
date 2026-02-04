from chimera.core.models import Task, TaskResult, TaskStatus
from chimera.mcp.client import SkillExecutor
import uuid
import asyncio

class WorkerAgent:
    """
    Worker Agent: Executes atomic tasks using MCP Skills.
    Stateless and ephemeral.
    """
    def __init__(self, worker_id: str = None):
        self.worker_id = worker_id or str(uuid.uuid4())
        self.skill_executor = SkillExecutor()

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Executes the assigned task.
        """
        print(f"[{self.worker_id}] Starting Task {task.task_id}: {task.task_type}")
        
        try:
            # Simulate work logic mapping Task -> Skill Call
            # In a real system, an LLM would decide which tool to call.
            # Here we follow a deterministic path for the prototype.
            
            output = {}
            if task.task_type == "generate_content":
                # Mock call to generate_image
                output = self.skill_executor.execute_tool("generate_image", {
                    "prompt": task.context.goal_description,
                    "character_id": "chimera_v1"
                })
            elif task.task_type == "social_action":
                output = self.skill_executor.execute_tool("post_tweet", {
                    "content": task.context.goal_description
                })
            
            return TaskResult(
                task_id=task.task_id,
                worker_id=self.worker_id,
                output=output,
                confidence_score=0.95, # Mock high confidence
                status="success"
            )
            
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                worker_id=self.worker_id,
                output={"error": str(e)},
                confidence_score=0.0,
                status="failed"
            )

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from chimera.core.models import Task, TaskResult, TaskStatus
from chimera.mcp.client import SkillExecutor
from chimera.core.llm import LLMClient
import uuid
import asyncio

class ToolSelection(BaseModel):
    """Structured output for tool selection."""
    tool_name: str = Field(description="The name of the tool to call")
    arguments: Dict[str, Any] = Field(description="Arguments for the tool")
    reasoning: str = Field(description="Why this tool was selected")

class WorkerAgent:
    """
    Worker Agent: Executes atomic tasks using MCP Skills.
    Stateless and ephemeral.
    Uses LLM to dynamically select and execute tools.
    """
    def __init__(self, worker_id: str = None, server_script_path: str = None):
        self.worker_id = worker_id or str(uuid.uuid4())
        if server_script_path:
            self.skill_executor = SkillExecutor(server_script_path=server_script_path)
        else:
            self.skill_executor = SkillExecutor()
        self.llm = LLMClient()

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Executes the assigned task by finding the right tool.
        """
        print(f"[{self.worker_id}] Starting Task {task.task_id}: {task.task_type}")
        
        try:
            # 1. Discover capabilities
            tools = await self.skill_executor.list_tools()
            
            if not tools:
                # Fallback if no tools avail (or server not running)
                # For prototype, we might want to warn or try start server
                print(f"[{self.worker_id}] Warning: No tools found via MCP.")
            
            tool_definitions = "\n".join([f"- {t.name}: {t.description}" for t in tools]) if tools else "No tools available."
            
            # 2. Decide on action (LLM)
            system_prompt = f"""
            You are a Worker Agent for Project Chimera. 
            Your job is to execute the assigned task using one of the available tools.
            
            Available Tools:
            {tool_definitions}
            
            Select the most appropriate tool and provide the necessary arguments based on the tool's schema.
            If no tool fits perfectly, choose the closest one or standard fallback.
            """
            
            prompt = f"""
            Task Context:
            Type: {task.task_type}
            Goal: {task.context.goal_description}
            Constraints: {task.context.persona_constraints}
            """
            
            print(f"[{self.worker_id}] Thinking... (Asking LLM to select tool)")
            
            selection: ToolSelection = await self.llm.generate_structured(
                prompt=prompt,
                response_model=ToolSelection,
                system_instruction=system_prompt
            )
            
            print(f"[{self.worker_id}] Selected Tool: {selection.tool_name}")
            print(f"[{self.worker_id}] Reasoning: {selection.reasoning}")
            
            # 3. Execute
            output = await self.skill_executor.execute_tool(
                selection.tool_name, 
                selection.arguments
            )
            
            status = "success"
            if output.get("status") == "failed":
                status = "failed"
            
            return TaskResult(
                task_id=task.task_id,
                worker_id=self.worker_id,
                output=output,
                confidence_score=0.95, # In real system, agent would self-evaluate
                status=status
            )
            
        except Exception as e:
            print(f"[{self.worker_id}] Error: {e}")
            return TaskResult(
                task_id=task.task_id,
                worker_id=self.worker_id,
                output={"error": str(e)},
                confidence_score=0.0,
                status="failed"
            )
        finally:
            try:
                await self.skill_executor.cleanup()
            except Exception:
                pass

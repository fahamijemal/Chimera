from typing import List, Dict, Any
import logging
import asyncio
from pydantic import BaseModel
from chimera.core.models import Task
from chimera.core.llm import LLMClient
from chimera.mcp.client import SkillExecutor
from chimera.core.perception import NewsIngester

logger = logging.getLogger(__name__)

class TaskList(BaseModel):
    """Container for list of tasks to support structured output."""
    tasks: List[Task]

class PlannerAgent:
    """
    Planner Agent: Decomposes goals into tasks using LLM.
    Now capable of Autonomous Perception-Action Loops.
    """
    def __init__(self):
        self.llm = LLMClient()
        self.news_ingester = NewsIngester()
        
    async def run_autonomous_loop(self) -> Dict[str, Any]:
        """
        Executes the autonomous Perception -> Reasoning -> Action loop.
        
        1. Perception: Fetches news from News Server.
        2. Reasoning: Decides on a concept based on news.
        3. Action: Generates an image using Image Server.
        """
        logger.info("[Planner] Starting Autonomous Loop...")
        results = {}
        
        # --- Step 1: Perception ---
        logger.info("[Planner] 1. Perception: Fetching News...")
        news_client = SkillExecutor(server_script_path="./chimera/mcp/servers/news_server.py")
        try:
            news_result = await news_client.read_resource("news://latest")
            if news_result["status"] == "success":
                raw_news = news_result["content"]
                # Parse for structured usage (optional, but good for logging)
                parsed_items = self.news_ingester.parse_mcp_news_response(raw_news)
                results["news_count"] = len(parsed_items)
                results["top_headline"] = parsed_items[0]["title"] if parsed_items else "No news"
            else:
                logger.error(f"Failed to fetch news: {news_result.get('error')}")
                return {"status": "failed", "step": "perception", "error": news_result.get("error")}
        finally:
            await news_client.cleanup()
            
        # --- Step 2: Reasoning ---
        logger.info(f"[Planner] 2. Reasoning: Analyzing {results['news_count']} headlines...")
        
        prompt = f"""
        Based on the following tech news headlines, create a creative prompt for an image generation model.
        The image should abstractly represent the most interesting trend or story.
        
        HEADLINES:
        {raw_news}
        
        OUTPUT:
        Just the image prompt string.
        """
        
        try:
            # Simple generate_content call (not structured)
            image_prompt = await self.llm.generate_response(prompt)
            image_prompt = image_prompt.strip()
            results["generated_prompt"] = image_prompt
            logger.info(f"[Planner] Generated Prompt: {image_prompt}")
        except Exception as e:
             logger.error(f"LLM Reasoning failed: {e}")
             return {"status": "failed", "step": "reasoning", "error": str(e)}

        # --- Step 3: Action ---
        logger.info("[Planner] 3. Action: Generating Image...")
        image_client = SkillExecutor(server_script_path="./chimera/mcp/servers/image_server.py")
        try:
            action_result = await image_client.execute_tool(
                "generate_image", 
                {"prompt": image_prompt, "character_id": "planner_auto"}
            )
            
            if action_result["status"] == "success":
                # The tool returns a JSON string or dict depending on implementation
                # FastMCP usually returns text. Our image_server returns a dict str representation?
                # Actually execute_tool helper extracts text.
                # Let's trust the logged output for now or parse if needed.
                results["image_result"] = action_result["result"]
                logger.info(f"[Planner] Image Generation Result: {action_result['result']}")
            else:
                logger.error(f"Image generation failed: {action_result.get('error')}")
                return {"status": "failed", "step": "action", "error": action_result.get("error")}
                
        finally:
            await image_client.cleanup()

        results["status"] = "success"
        return results

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


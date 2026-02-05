"""
Central Orchestrator for the Chimera Network.

Manages the lifecycle of the agent swarm using the FastRender Pattern.
This is the "operating system" of the Chimera network.
"""
from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime

from chimera.core.state import StateManager, GlobalState
from chimera.core.queues import QueueManager
from chimera.agents.planner import PlannerAgent
from chimera.agents.worker import WorkerAgent
from chimera.agents.judge import JudgeAgent
from chimera.agents.cfo_judge import CFOJudge
from chimera.core.models import Task, TaskResult, TaskType, Verdict

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central Orchestrator managing the Planner-Worker-Judge swarm.
    
    Responsibilities:
    - Manages GlobalState
    - Coordinates task flow (Planner -> Worker -> Judge)
    - Handles HITL escalation
    - Monitors swarm health
    """
    
    def __init__(
        self,
        state_manager: Optional[StateManager] = None,
        queue_manager: Optional[QueueManager] = None,
        num_workers: int = 3
    ):
        """
        Initialize Orchestrator.
        
        Args:
            state_manager: GlobalState manager (creates new if None)
            queue_manager: Queue manager (creates new if None)
            num_workers: Number of worker agents to spawn
        """
        self.state_manager = state_manager or StateManager()
        self.queue_manager = queue_manager or QueueManager()
        
        # Initialize agents
        self.planner = PlannerAgent()
        self.judge = JudgeAgent()
        self.cfo_judge = CFOJudge(self.state_manager)
        
        # Worker pool
        self.workers: List[WorkerAgent] = [
            WorkerAgent() for _ in range(num_workers)
        ]
        
        # HITL queue (for medium confidence tasks)
        self.hitl_queue: List[TaskResult] = []
        
        # Running state
        self._running = False
        self._tasks: List[asyncio.Task] = []
    
    async def initialize(self):
        """Initializes connections (Redis, etc.)."""
        await self.queue_manager.connect()
        logger.info("Orchestrator initialized")
    
    async def shutdown(self):
        """Gracefully shuts down the orchestrator."""
        self._running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Disconnect queues
        await self.queue_manager.disconnect()
        
        logger.info("Orchestrator shut down")
    
    async def start_campaign(self, goal_description: str, campaign_id: str) -> bool:
        """
        Starts a new campaign by adding it to GlobalState.
        
        Args:
            goal_description: High-level goal (e.g., "Promote summer fashion line")
            campaign_id: Unique campaign identifier
            
        Returns:
            True if campaign started successfully
        """
        campaign_data = {
            "goal_description": goal_description,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        success = self.state_manager.add_campaign(campaign_id, campaign_data, "orchestrator")
        
        if success:
            logger.info(f"Campaign {campaign_id} started: {goal_description}")
            # Trigger planner to decompose goal
            tasks = self.planner.decompose_goal(goal_description)
            for task in tasks:
                await self.queue_manager.push_task(task)
        
        return success
    
    async def run_planner_loop(self):
        """
        Planner loop: Monitors GlobalState and creates tasks.
        
        This runs continuously, checking for new goals and creating tasks.
        """
        logger.info("Planner loop started")
        
        while self._running:
            try:
                # Get current state
                state = self.state_manager.get_state_snapshot()
                
                # Check for active campaigns
                for campaign_id, campaign_data in state.active_campaigns.items():
                    if campaign_data.get("status") == "active":
                        goal = campaign_data.get("goal_description", "")
                        
                        # Decompose goal into tasks
                        tasks = self.planner.decompose_goal(goal)
                        
                        # Push tasks to queue
                        for task in tasks:
                            await self.queue_manager.push_task(task)
                            logger.debug(f"Planner: Created task {task.task_id} for campaign {campaign_id}")
                
                # Sleep before next iteration
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Planner loop error: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def run_worker_loop(self, worker: WorkerAgent):
        """
        Worker loop: Pops tasks, executes them, pushes results.
        
        Args:
            worker: Worker agent instance
        """
        logger.info(f"Worker {worker.worker_id} loop started")
        
        while self._running:
            try:
                # Pop task from queue
                task = await self.queue_manager.pop_task(timeout=5)
                
                if task is None:
                    continue  # Timeout, try again
                
                # Execute task
                result = await worker.execute_task(task)
                
                # Push result to review queue
                await self.queue_manager.push_result(result)
                
                logger.debug(f"Worker {worker.worker_id}: Completed task {task.task_id}")
                
            except Exception as e:
                logger.error(f"Worker {worker.worker_id} loop error: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def run_judge_loop(self):
        """
        Judge loop: Pops results, validates them, commits or escalates.
        
        This implements the HITL confidence-based routing.
        """
        logger.info("Judge loop started")
        
        while self._running:
            try:
                # Pop result from review queue
                result = await self.queue_manager.pop_result(timeout=5)
                
                if result is None:
                    continue  # Timeout, try again
                
                # Select appropriate judge based on task type
                if result.output.get("transaction"):
                    # Financial transaction - use CFO Judge
                    decision = self.cfo_judge.evaluate(result)
                else:
                    # Regular content - use standard Judge
                    decision = self.judge.evaluate(result)
                
                # Route based on verdict
                if decision.verdict == Verdict.APPROVE:
                    # Auto-approve: Commit to state
                    logger.info(f"Judge: APPROVED result for task {result.task_id}")
                    # In production, would update GlobalState here
                    
                elif decision.verdict == Verdict.ESCALATE:
                    # Medium confidence: Add to HITL queue
                    self.hitl_queue.append(result)
                    logger.info(f"Judge: ESCALATED result for task {result.task_id} to HITL")
                    
                elif decision.verdict == Verdict.REJECT:
                    # Low confidence: Reject and signal planner to retry
                    logger.warning(f"Judge: REJECTED result for task {result.task_id}: {decision.reason}")
                    # In production, would signal planner to create new task
                
            except Exception as e:
                logger.error(f"Judge loop error: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def start(self):
        """Starts all orchestrator loops."""
        self._running = True
        
        # Start planner loop
        self._tasks.append(asyncio.create_task(self.run_planner_loop()))
        
        # Start worker loops
        for worker in self.workers:
            self._tasks.append(asyncio.create_task(self.run_worker_loop(worker)))
        
        # Start judge loop
        self._tasks.append(asyncio.create_task(self.run_judge_loop()))
        
        logger.info(f"Orchestrator started with {len(self.workers)} workers")
    
    def get_hitl_queue(self) -> List[TaskResult]:
        """Returns the current HITL queue for human review."""
        return self.hitl_queue.copy()
    
    def approve_hitl_task(self, task_id: str) -> bool:
        """Approves a task from the HITL queue."""
        for i, result in enumerate(self.hitl_queue):
            if result.task_id == task_id:
                self.hitl_queue.pop(i)
                logger.info(f"HITL: Approved task {task_id}")
                # In production, would commit to state here
                return True
        return False
    
    def reject_hitl_task(self, task_id: str) -> bool:
        """Rejects a task from the HITL queue."""
        for i, result in enumerate(self.hitl_queue):
            if result.task_id == task_id:
                self.hitl_queue.pop(i)
                logger.info(f"HITL: Rejected task {task_id}")
                # In production, would signal planner to retry
                return True
        return False

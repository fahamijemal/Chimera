from typing import List
from chimera.core.models import Task, TaskType, TaskContext, TaskPriority

class PlannerAgent:
    """
    Planner Agent: Decomposes goals into tasks.
    """
    def decompose_goal(self, goal: str) -> List[Task]:
        """
        Takes a high-level goal and returns a list of Tasks.
        """
        print(f"[Planner] Decomposing goal: {goal}")
        
        # simple heuristic for prototype
        tasks = []
        
        # 1. Create content
        tasks.append(Task(
            task_type=TaskType.GENERATE_CONTENT,
            priority=TaskPriority.HIGH,
            context=TaskContext(
                goal_description=f"Visual for: {goal}",
                persona_constraints=["Cyberpunk"]
            )
        ))
        
        # 2. Post content
        tasks.append(Task(
            task_type=TaskType.SOCIAL_ACTION,
            priority=TaskPriority.MEDIUM,
            context=TaskContext(
                goal_description=f"Social post for: {goal}"
            )
        ))
        
        return tasks

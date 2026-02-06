"""
Manual test script for Planner LLM integration.
"""
import logging
from chimera.agents.planner import PlannerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    print("Initializing Planner Agent...")
    planner = PlannerAgent()
    
    goal = "Create a viral marketing campaign for a new cyberpunk coffee shop launch in Tokyo."
    print(f"\nDecomposing Goal: {goal}")
    print("-" * 50)
    
    tasks = planner.decompose_goal(goal)
    
    if not tasks:
        print("❌ No tasks returned (Ensure GEMINI_API_KEY is set)")
    else:
        print(f"✅ Successfully generated {len(tasks)} tasks:\n")
        for i, task in enumerate(tasks, 1):
            print(f"Task {i}: [{task.task_type.value}] ({task.priority.value})")
            print(f"  Context: {task.context.goal_description}")
            if task.context.persona_constraints:
                print(f"  Constraints: {task.context.persona_constraints}")
            print()

if __name__ == "__main__":
    main()

from chimera.core.models import TaskResult

class JudgeAgent:
    """
    Judge Agent: Validates outputs and manages state transitions.
    """
    def evaluate_result(self, result: TaskResult) -> str:
        """
        Decides the fate of a result: APPROVE, REJECT, ESCALATE.
        """
        print(f"[Judge] Evaluating result from Worker {result.worker_id}")
        
        if result.status == "failed":
            return "REJECT"
            
        # Confidence logic (Management by Exception)
        if result.confidence_score > 0.9:
            return "APPROVE"
        elif result.confidence_score > 0.7:
            return "ESCALATE"
        else:
            return "REJECT"

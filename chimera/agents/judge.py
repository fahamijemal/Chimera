from chimera.core.models import TaskResult, Verdict
from pydantic import BaseModel

class JudgeDecision(BaseModel):
    verdict: Verdict
    reason: str = ""

class JudgeAgent:
    """
    Judge Agent: Validates outputs and manages state transitions.
    """
    def evaluate(self, result: TaskResult) -> JudgeDecision:
        """
        Decides the fate of a result: APPROVE, REJECT, ESCALATE.
        """
        print(f"[Judge] Evaluating result from Worker {result.worker_id}")
        
        if result.status == "failed":
            return JudgeDecision(verdict=Verdict.REJECT, reason="Task failed execution")
            
        # Confidence logic (Management by Exception)
        if result.confidence_score >= 0.9:
            return JudgeDecision(verdict=Verdict.APPROVE, reason="High confidence")
        elif result.confidence_score >= 0.7:
            return JudgeDecision(verdict=Verdict.ESCALATE, reason="Medium confidence, needs review")
        else:
            return JudgeDecision(verdict=Verdict.REJECT, reason="Low confidence")

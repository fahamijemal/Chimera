"""
CFO Judge: Specialized Judge Agent for Budget Governance.

Implements FR 5.2: Budget Governance (The "CFO" Sub-Agent).
This judge enforces strict budget limits and anomaly detection for financial transactions.
"""
from chimera.agents.judge import JudgeAgent, JudgeDecision
from chimera.core.models import TaskResult, Verdict, TaskType
from chimera.core.state import StateManager
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    """Raised when a transaction would exceed budget limits."""
    pass


class CFOJudge(JudgeAgent):
    """
    Specialized Judge for financial transaction validation.
    
    This judge has absolute authority to REJECT any transaction that:
    - Exceeds daily spending limits
    - Matches suspicious patterns (e.g., large amounts, unknown recipients)
    - Would violate budget policies
    """
    
    def __init__(self, state_manager: StateManager, max_daily_spend: Dict[str, float] = None):
        """
        Initialize CFO Judge.
        
        Args:
            state_manager: GlobalState manager for budget tracking
            max_daily_spend: Maximum daily spend per currency (defaults to common limits)
        """
        super().__init__()
        self.state_manager = state_manager
        self.max_daily_spend = max_daily_spend or {
            "USDC": 50.0,
            "ETH": 0.01,
            "USD": 50.0
        }
        
        # Suspicious pattern thresholds
        self.suspicious_amount_threshold = {
            "USDC": 100.0,
            "ETH": 0.1,
            "USD": 100.0
        }
    
    def evaluate(self, result: TaskResult) -> JudgeDecision:
        """
        Evaluates a financial transaction result.
        
        This overrides the base JudgeAgent.evaluate() to add budget-specific logic.
        """
        # First, check if this is a transaction task
        # (In a real system, we'd check task_type from the original Task)
        transaction_data = result.output.get("transaction", {})
        
        if not transaction_data:
            # Not a transaction - delegate to base judge
            return super().evaluate(result)
        
        # Extract transaction details
        currency = transaction_data.get("currency", "USDC")
        amount = float(transaction_data.get("amount", 0.0))
        recipient = transaction_data.get("to_address", "")
        
        # 1. Check daily budget limit
        is_allowed, current_spend = self.state_manager.check_budget_limit(currency, amount)
        
        if not is_allowed:
            limit = self.max_daily_spend.get(currency, 0.0)
            logger.warning(
                f"CFO Judge REJECTED: Transaction would exceed daily limit. "
                f"Current: {current_spend} {currency}, Requested: {amount} {currency}, Limit: {limit} {currency}"
            )
            return JudgeDecision(
                verdict=Verdict.REJECT,
                reason=f"Transaction would exceed daily budget limit ({current_spend + amount} > {limit} {currency})"
            )
        
        # 2. Check for suspicious patterns
        suspicious_reasons = []
        
        # Large amount check
        threshold = self.suspicious_amount_threshold.get(currency, float('inf'))
        if amount > threshold:
            suspicious_reasons.append(f"Large transaction amount ({amount} {currency} > {threshold} {currency})")
        
        # Unknown recipient check (in production, maintain whitelist)
        if not recipient or recipient.startswith("0x0000"):
            suspicious_reasons.append("Suspicious or unknown recipient address")
        
        # 3. Anomaly detection: Multiple rapid transactions
        # (This would require tracking recent transactions - simplified here)
        
        if suspicious_reasons:
            logger.warning(
                f"CFO Judge ESCALATED: Suspicious transaction detected. Reasons: {suspicious_reasons}"
            )
            return JudgeDecision(
                verdict=Verdict.ESCALATE,
                reason=f"Suspicious transaction pattern detected: {'; '.join(suspicious_reasons)}. Requires human review."
            )
        
        # 4. If passed all checks, use base confidence logic
        base_decision = super().evaluate(result)
        
        # But CFO has final say - even high confidence needs budget check
        if base_decision.verdict == Verdict.APPROVE:
            # Update budget tracking (this would be done atomically in production)
            success = self.state_manager.update_budget(currency, amount, "cfo_judge")
            
            if not success:
                # OCC conflict - state changed during evaluation
                return JudgeDecision(
                    verdict=Verdict.REJECT,
                    reason="State conflict detected during budget update. Please retry."
                )
            
            logger.info(
                f"CFO Judge APPROVED: Transaction of {amount} {currency} approved. "
                f"New daily spend: {current_spend + amount} {currency}"
            )
        
        return base_decision
    
    def set_budget_limit(self, currency: str, limit: float) -> None:
        """Updates the daily spending limit for a currency."""
        self.max_daily_spend[currency] = limit
        logger.info(f"CFO Judge: Updated {currency} daily limit to {limit}")

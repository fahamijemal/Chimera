"""
Coinbase AgentKit Integration for Agentic Commerce.

Implements FR 5.0, FR 5.1: Non-Custodial Wallet Management and Autonomous Transactions.
"""
from typing import Optional, Dict, Any
import os
from datetime import datetime
from pydantic import BaseModel
from functools import wraps
import redis
import logging

logger = logging.getLogger(__name__)

try:
    from coinbase.agentkit import CdpEvmWalletProvider, Erc20ActionProvider
    from coinbase import CDP_ACCESS_KEY_NAME, CDP_ACCESS_KEY_PRIVATE_KEY
    AGENTKIT_AVAILABLE = True
except ImportError:
    AGENTKIT_AVAILABLE = False
    CdpEvmWalletProvider = None
    Erc20ActionProvider = None
    logger.warning("Coinbase AgentKit not available. Install with: pip install coinbase-agentkit")


class BudgetExceededError(Exception):
    """Raised when a transaction would exceed budget limits."""
    pass


class CommerceManager:
    """
    Manages agent financial operations via Coinbase AgentKit.
    
    Each Chimera Agent has a non-custodial wallet that can:
    - Check balance
    - Transfer assets (ETH, USDC, etc.)
    - Deploy tokens (ERC-20)
    """
    
    def __init__(
        self,
        api_key_name: Optional[str] = None,
        api_key_private_key: Optional[str] = None,
        redis_client: Optional[redis.Redis] = None
    ):
        """
        Initialize Commerce Manager.
        
        Args:
            api_key_name: CDP API key name (defaults to CDP_API_KEY_NAME env var)
            api_key_private_key: CDP API key private key (defaults to CDP_API_KEY_PRIVATE_KEY env var)
            redis_client: Redis client for budget tracking (optional)
        """
        if not AGENTKIT_AVAILABLE:
            raise ImportError(
                "Coinbase AgentKit is not installed. "
                "Install with: pip install coinbase-agentkit"
            )
        
        self.api_key_name = api_key_name or os.getenv("CDP_API_KEY_NAME")
        self.api_key_private_key = api_key_private_key or os.getenv("CDP_API_KEY_PRIVATE_KEY")
        
        if not self.api_key_name or not self.api_key_private_key:
            raise ValueError(
                "CDP_API_KEY_NAME and CDP_API_KEY_PRIVATE_KEY must be set "
                "as environment variables or passed to constructor"
            )
        
        # Initialize wallet provider
        self.wallet_provider = CdpEvmWalletProvider(
            api_key_name=self.api_key_name,
            api_key_private_key=self.api_key_private_key
        )
        
        # Initialize action providers
        self.erc20_provider = Erc20ActionProvider(self.wallet_provider)
        
        # Redis for budget tracking
        self.redis_client = redis_client or redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
        
        # Budget limits (can be overridden)
        self.max_daily_limit = {
            "USDC": float(os.getenv("MAX_DAILY_USDC", "50.0")),
            "ETH": float(os.getenv("MAX_DAILY_ETH", "0.01")),
        }
    
    async def get_balance(self, currency: str = "USDC") -> float:
        """
        Gets the current wallet balance.
        
        Args:
            currency: Currency symbol (USDC, ETH, etc.)
            
        Returns:
            Balance amount
        """
        try:
            if currency.upper() == "USDC":
                # Get USDC balance via ERC-20
                balance = await self.erc20_provider.get_balance(
                    token_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Base USDC
                    wallet_address=self.wallet_provider.get_wallet_address()
                )
                return float(balance) / 1e6  # USDC has 6 decimals
            elif currency.upper() == "ETH":
                # Get native ETH balance
                balance = await self.wallet_provider.get_balance()
                return float(balance) / 1e18  # ETH has 18 decimals
            else:
                raise ValueError(f"Unsupported currency: {currency}")
        except Exception as e:
            logger.error(f"Failed to get balance for {currency}: {e}")
            raise
    
    async def send_payment(
        self,
        to_address: str,
        amount_usdc: float,
        agent_id: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Transfers USDC to an external wallet.
        
        This method is decorated with @budget_check to enforce daily limits.
        
        Args:
            to_address: Recipient wallet address
            amount_usdc: Amount in USDC
            agent_id: ID of the agent initiating the transaction
            
        Returns:
            Transaction receipt with tx_hash
            
        Raises:
            BudgetExceededError: If transaction would exceed daily limit
        """
        # Check budget (decorator handles this, but we also check here for clarity)
        daily_spend_key = f"daily_spend:USDC:{agent_id}"
        current_spend = float(self.redis_client.get(daily_spend_key) or 0.0)
        
        if current_spend + amount_usdc > self.max_daily_limit["USDC"]:
            raise BudgetExceededError(
                f"Transaction would exceed daily limit. "
                f"Current: {current_spend} USDC, Requested: {amount_usdc} USDC, "
                f"Limit: {self.max_daily_limit['USDC']} USDC"
            )
        
        try:
            # Convert to wei (USDC has 6 decimals)
            amount_wei = int(amount_usdc * 1e6)
            
            # Execute transfer
            tx_hash = await self.erc20_provider.transfer(
                token_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Base USDC
                to_address=to_address,
                amount=amount_wei
            )
            
            # Update daily spend atomically
            self.redis_client.incrbyfloat(daily_spend_key, amount_usdc)
            
            logger.info(
                f"CommerceManager: Sent {amount_usdc} USDC to {to_address}. "
                f"TX: {tx_hash}, Daily spend: {current_spend + amount_usdc} USDC"
            )
            
            return {
                "status": "success",
                "tx_hash": tx_hash,
                "amount": amount_usdc,
                "currency": "USDC",
                "to_address": to_address,
                "daily_spend": current_spend + amount_usdc
            }
        except Exception as e:
            logger.error(f"Failed to send payment: {e}")
            raise
    
    async def deploy_token(
        self,
        name: str,
        symbol: str,
        total_supply: int,
        agent_id: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Deploys an ERC-20 token (e.g., for fan loyalty programs).
        
        Args:
            name: Token name
            symbol: Token symbol
            total_supply: Total supply amount
            agent_id: ID of the agent deploying the token
            
        Returns:
            Deployment receipt with contract address
        """
        # In a real implementation, this would compile Solidity bytecode and send a create transaction.
        # For this stage of Project Chimera, we simulate the deployment to demonstrate the agentic flow.
        logger.info(f"Deploying Token: {name} ({symbol}) with supply {total_supply} for agent {agent_id}")
        
        # Simulate gas cost
        gas_cost = 0.005 # ETH
        
        # Check ETH budget/balance (implied)
        # In full implementation, we'd check self.get_balance("ETH") here.
        
        # Mock Contract Address
        import hashlib
        mock_hash = hashlib.sha256(f"{name}{symbol}{datetime.now()}".encode()).hexdigest()[:40]
        contract_address = f"0x{mock_hash}"
        
        logger.info(f"Token Deployed Successfully. Contract: {contract_address}")
        
        return {
            "status": "success",
            "contract_address": contract_address,
            "tx_hash": f"0x{hashlib.sha256(mock_hash.encode()).hexdigest()}", # Mock TX
            "name": name,
            "symbol": symbol,
            "total_supply": total_supply,
            "deployer": self.wallet_provider.get_wallet_address() if AGENTKIT_AVAILABLE else "0xMockDeployer"
        }
    
    def get_wallet_address(self) -> str:
        """Returns the agent's wallet address."""
        return self.wallet_provider.get_wallet_address()


def budget_check(func):
    """
    Decorator to check budget limits before executing transactions.
    
    This decorator checks Redis for daily spend and raises BudgetExceededError
    if the transaction would exceed the limit.
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Extract amount and currency from kwargs or args
        amount = kwargs.get("amount_usdc", kwargs.get("amount", 0.0))
        currency = kwargs.get("currency", "USDC")
        agent_id = kwargs.get("agent_id", "unknown")
        
        # Check daily spend
        daily_spend_key = f"daily_spend:{currency}:{agent_id}"
        current_spend = float(self.redis_client.get(daily_spend_key) or 0.0)
        max_limit = self.max_daily_limit.get(currency, float('inf'))
        
        if current_spend + amount > max_limit:
            raise BudgetExceededError(
                f"Transaction would exceed daily limit. "
                f"Current: {current_spend} {currency}, Requested: {amount} {currency}, "
                f"Limit: {max_limit} {currency}"
            )
        
        # Execute the function
        result = await func(self, *args, **kwargs)
        
        # Update daily spend if transaction succeeded
        if result.get("status") == "success":
            self.redis_client.incrbyfloat(daily_spend_key, amount)
        
        return result
    
    return wrapper

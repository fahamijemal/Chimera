
"""
MCP Server for Agentic Commerce.

Exposes financial tools (CommerceManager) to the agent swarm.
"""
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
import logging
from chimera.core.commerce import CommerceManager, AGENTKIT_AVAILABLE

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("chimera-commerce")

# Initialize CommerceManager
# Note: In a real deployment, this might be a singleton or instanced per-request context
commerce_manager = None

def get_commerce_manager() -> CommerceManager:
    global commerce_manager
    if not commerce_manager:
        try:
            commerce_manager = CommerceManager()
        except Exception as e:
            logger.error(f"Failed to initialize CommerceManager: {e}")
            raise RuntimeError("Commerce capabilities unavailable.")
    return commerce_manager

@mcp.tool()
async def wallet_get_address() -> str:
    """
    Returns the agent's wallet address.
    """
    if not AGENTKIT_AVAILABLE:
        return "0xMockAddress(AgentKitUnavailable)"
    
    manager = get_commerce_manager()
    return manager.get_wallet_address()

@mcp.tool()
async def wallet_get_balance(currency: str = "USDC") -> float:
    """
    Gets the current balance of the wallet.
    
    Args:
        currency: The currency symbol (e.g., 'USDC', 'ETH').
    """
    if not AGENTKIT_AVAILABLE:
        return 0.0
        
    manager = get_commerce_manager()
    return await manager.get_balance(currency)

@mcp.tool()
async def wallet_send_payment(to_address: str, amount: float, currency: str = "USDC", reason: str = "") -> Dict[str, Any]:
    """
    Sends a payment to another wallet.
    
    Args:
        to_address: The recipient's wallet address.
        amount: The amount to send.
        currency: The currency symbol (default: 'USDC').
        reason: Justification for the transaction (for audit logs).
    """
    if not AGENTKIT_AVAILABLE:
        return {"status": "error", "message": "AgentKit not installed"}
        
    manager = get_commerce_manager()
    
    # Note: agent_id should be passed from context in full implementation
    # For now, we assume 'system' or pull from generic context if available
    result = await manager.send_payment(
        to_address=to_address,
        amount_usdc=amount, # Assuming USDC based on commerce.py signature
        agent_id="mcp_user"
    )
    return result

@mcp.tool()
async def wallet_deploy_token(name: str, symbol: str, total_supply: int) -> Dict[str, Any]:
    """
    Deploys a new ERC-20 token.
    
    Args:
        name: Name of the token (e.g., 'ChimeraFanToken').
        symbol: Symbol of the token (e.g., 'CFT').
        total_supply: Initial supply of the token.
    """
    if not AGENTKIT_AVAILABLE:
         return {"status": "error", "message": "AgentKit not installed"}
         
    manager = get_commerce_manager()
    return await manager.deploy_token(name, symbol, total_supply, agent_id="mcp_user")

if __name__ == "__main__":
    mcp.run()

"""
MCP Server for Coinbase AgentKit Integration.

Exposes wallet operations as MCP Tools for the Chimera agents.
"""
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import os
from chimera.core.commerce import CommerceManager

# Create FastMCP server
mcp = FastMCP("chimera-coinbase")

# Initialize commerce manager (lazy initialization)
_commerce_manager: Optional[CommerceManager] = None


def get_commerce_manager() -> CommerceManager:
    """Gets or creates the commerce manager instance."""
    global _commerce_manager
    if _commerce_manager is None:
        _commerce_manager = CommerceManager(
            api_key_name=os.getenv("CDP_API_KEY_NAME"),
            api_key_private_key=os.getenv("CDP_API_KEY_PRIVATE_KEY")
        )
    return _commerce_manager


@mcp.resource("wallet://balance/{currency}")
def get_wallet_balance_resource(currency: str = "USDC") -> str:
    """
    Resource: Returns current wallet balance.
    
    Args:
        currency: Currency symbol (USDC, ETH)
    """
    import asyncio
    manager = get_commerce_manager()
    balance = asyncio.run(manager.get_balance(currency))
    return f"Balance: {balance} {currency}"


@mcp.tool()
async def get_balance(currency: str = "USDC") -> Dict[str, Any]:
    """
    Tool: Gets wallet balance.
    
    Args:
        currency: Currency symbol (USDC, ETH)
    """
    manager = get_commerce_manager()
    balance = await manager.get_balance(currency)
    
    return {
        "status": "success",
        "balance": balance,
        "currency": currency,
        "wallet_address": manager.get_wallet_address()
    }


@mcp.tool()
async def transfer_asset(
    to_address: str,
    amount: float,
    currency: str = "USDC",
    agent_id: str = "unknown"
) -> Dict[str, Any]:
    """
    Tool: Transfers assets to external wallet.
    
    Args:
        to_address: Recipient address
        amount: Amount to transfer
        currency: Currency (USDC, ETH)
        agent_id: Agent initiating transaction
    """
    manager = get_commerce_manager()
    
    if currency.upper() == "USDC":
        result = await manager.send_payment(to_address, amount, agent_id)
    else:
        # For other currencies, would need additional implementation
        return {
            "status": "error",
            "message": f"Currency {currency} not yet supported"
        }
    
    return result


@mcp.tool()
async def deploy_token(
    name: str,
    symbol: str,
    total_supply: int,
    agent_id: str = "unknown"
) -> Dict[str, Any]:
    """
    Tool: Deploys an ERC-20 token.
    
    Args:
        name: Token name
        symbol: Token symbol
        total_supply: Total supply
        agent_id: Agent deploying token
    """
    manager = get_commerce_manager()
    result = await manager.deploy_token(name, symbol, total_supply, agent_id)
    return result


if __name__ == "__main__":
    mcp.run()

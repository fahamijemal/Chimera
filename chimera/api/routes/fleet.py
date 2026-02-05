from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class WalletBalance(BaseModel):
    eth: float
    usdc: float

class AgentStatus(BaseModel):
    id: str
    name: str
    role: str
    info: str
    status: str
    wallet_balance: WalletBalance

@router.get("/status", response_model=List[AgentStatus])
async def get_fleet_status():
    """
    Returns the real-time status of the agent fleet.
    For Day 2 demo, this returns mock data mimicking a live system.
    In the future, this will query Redis/GlobalState.
    """
    return [
        {
            "id": "agent-planner-01",
            "name": "Strategist Prime",
            "role": "Planner",
            "info": "Analyzing 'Summer 2026' trends",
            "status": "active",
            "wallet_balance": {"eth": 0.05, "usdc": 120.00}
        },
        {
            "id": "agent-worker-01",
            "name": "Content Gen Alpha",
            "role": "Worker",
            "info": "Generating image for #ChimeraDrop",
            "status": "active",
            "wallet_balance": {"eth": 0.01, "usdc": 15.50}
        },
        {
            "id": "agent-worker-02",
            "name": "Social Interaction Bot",
            "role": "Worker",
            "info": "Replying to comments on Post #882",
            "status": "idle",
            "wallet_balance": {"eth": 0.01, "usdc": 45.00}
        },
        {
            "id": "agent-judge-cfo",
            "name": "The CFO",
            "role": "Judge",
            "info": "Monitoring transaction thresholds",
            "status": "active",
            "wallet_balance": {"eth": 0.10, "usdc": 5000.00}
        }
    ]

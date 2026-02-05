"""
PostgreSQL Database Models and Schema.

Implements the database schema as specified in specs/technical.md.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(BaseModel):
    """Campaign model for PostgreSQL."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_description: str
    status: CampaignStatus = CampaignStatus.ACTIVE
    budget_limit: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class TaskRecord(BaseModel):
    """Task record model for PostgreSQL."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    worker_type: str  # "planner", "worker", "judge"
    status: str  # "pending", "processing", "review", "complete", "failed"
    result_artifact: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Transaction(BaseModel):
    """Transaction record model for PostgreSQL."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_address: str
    amount: float
    currency: str = "USDC"
    tx_hash: Optional[str] = None
    status: str = "pending"  # "pending", "confirmed", "failed"
    created_at: datetime = Field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# SQL Schema (for migration scripts)
POSTGRES_SCHEMA = """
-- Campaigns Table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    budget_limit DECIMAL(18, 8) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    worker_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    result_artifact JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_address VARCHAR(42) NOT NULL,
    amount DECIMAL(18, 8) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USDC',
    tx_hash VARCHAR(66),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_campaign_id ON tasks(campaign_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_transactions_wallet ON transactions(wallet_address);
CREATE INDEX IF NOT EXISTS idx_transactions_tx_hash ON transactions(tx_hash);
"""

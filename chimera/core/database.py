"""
PostgreSQL Database Models and Schema.

Implements the database schema as specified in specs/technical.md.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
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
    
    model_config = ConfigDict(from_attributes=True)


class TaskRecord(BaseModel):
    """Task record model for PostgreSQL."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    worker_type: str  # "planner", "worker", "judge"
    status: str  # "pending", "processing", "review", "complete", "failed"
    result_artifact: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


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
    
    model_config = ConfigDict(from_attributes=True)


# SQL Schema (for migration scripts)

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

# Database Connection Logic
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages asynchronous connections to PostgreSQL.
    """
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Postgres connection string (defaults to POSTGRES_URL env var)
        """
        self.database_url = database_url or os.getenv("POSTGRES_URL")
        # Ensure we use the async driver
        if self.database_url and self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
            
        self.engine = None
        self.session_factory = None
        
    async def connect(self):
        """Creates the async engine and session factory."""
        if not self.database_url:
            logger.warning("No database URL configured. Using mock mode.")
            return

        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG",
                future=True,
                pool_pre_ping=True
            )
            self.session_factory = sessionmaker(
                self.engine, 
                expire_on_commit=False, 
                class_=AsyncSession
            )
            logger.info("Database connection initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.engine = None

    async def disconnect(self):
        """Closes the engine."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed.")

    async def init_db(self):
        """Initialize database schema."""
        if not self.engine:
            return
            
        async with self.engine.begin() as conn:
            # Execute raw SQL schema
            # Note: In production you'd use Alembic. This is for bootstrapping.
            for statement in POSTGRES_SCHEMA.split(';'):
                if statement.strip():
                    await conn.execute(text(statement))
            logger.info("Database schema initialized.")

    async def get_session(self) -> AsyncSession:
        """Dependency for getting a DB session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call connect() first.")
            
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

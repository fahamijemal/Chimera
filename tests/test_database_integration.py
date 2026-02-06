
import pytest
import os
from chimera.core.database import DatabaseManager, Campaign, CampaignStatus

# Mark as integration test
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def db_manager():
    # Allow override for test DB
    url = os.getenv("POSTGRES_TEST_URL", os.getenv("POSTGRES_URL"))
    if not url:
        pytest.skip("POSTGRES_URL not set")
    
    manager = DatabaseManager(url)
    await manager.connect()
    # Initialize schema for test
    await manager.init_db()
    yield manager
    await manager.disconnect()

async def test_campaign_crud(db_manager):
    """Test creating and retrieving a campaign."""
    async with db_manager.session_factory() as session:
        # Create
        campaign = Campaign(
            goal_description="Integration Test Campaign",
            status=CampaignStatus.ACTIVE,
            budget_limit=100.0
        )
        
        # We need to map Pydantic model to SQLAlchemy ORM if we were using full ORM
        # simpler validation: usage with raw sql or minimal wrapper for now 
        # since we haven't defined full SQLAlchemy ORM mapped classes in `models.py` yet
        # checking implementation in database.py shows we initialized tables via raw SQL.
        
        # Let's insert via raw SQL for this integration test since ORM mappings aren't fully set up in the snippet
        from sqlalchemy import text
        
        await session.execute(
            text("INSERT INTO campaigns (id, goal_description, status, budget_limit) VALUES (:id, :goal, :status, :budget)"),
            {
                "id": campaign.id,
                "goal": campaign.goal_description,
                "status": campaign.status.value,
                "budget": campaign.budget_limit
            }
        )
        await session.commit()
        
        # Read
        result = await session.execute(
            text("SELECT * FROM campaigns WHERE id = :id"),
            {"id": campaign.id}
        )
        row = result.fetchone()
        
        assert row is not None
        assert row.goal_description == "Integration Test Campaign"
        assert float(row.budget_limit) == 100.0


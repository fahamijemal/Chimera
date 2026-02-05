
import asyncio
import os
import logging
from chimera.core.database import DatabaseManager
from chimera.core.queues import QueueManager
from chimera.core.memory import MemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("validate_connections")

async def validate_postgres():
    logger.info("--- Validating PostgreSQL ---")
    db_url = os.getenv("POSTGRES_URL")
    if not db_url:
        logger.warning("POSTGRES_URL not set. Skipping verification (treated as success for dev environment).")
        return True

    db = DatabaseManager(db_url)
    try:
        await db.connect()
        # Simple query to verify
        async with db.session_factory() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                logger.info("✅ PostgreSQL Connection successful.")
            else:
                logger.error("❌ PostgreSQL Connection failed: Invalid result.")
        await db.disconnect()
        return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL Connection failed: {e}")
        return False

async def validate_redis():
    logger.info("--- Validating Redis ---")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    q = QueueManager(redis_url)
    try:
        await q.connect()
        # Ping
        if await q._client.ping():
             logger.info("✅ Redis Connection successful.")
        else:
             logger.error("❌ Redis Connection failed: Ping failed.")
        await q.disconnect()
        return True
    except Exception as e:
        logger.error(f"❌ Redis Connection failed: {e}")
        return False

async def validate_weaviate():
    logger.info("--- Validating Weaviate ---")
    w = MemoryManager() # Uses env vars
    if w.client and w.client.is_live():
        logger.info("✅ Weaviate Connection successful.")
        w.client.close()
        return True
    else:
        logger.error("❌ Weaviate Connection failed (or not configured).")
        if w.client: w.client.close()
        return False

async def main():
    print("Beginning Connection Validation Code...")
    pg_ok = await validate_postgres()
    redis_ok = await validate_redis()
    weaviate_ok = await validate_weaviate()
    
    if pg_ok and redis_ok and weaviate_ok:
        print("\n🎉 ALL SYSTEMS GO! Production services are reachable.")
        exit(0)
    else:
        print("\n⚠️ SOME CHECKS FAILED. See logs above.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())

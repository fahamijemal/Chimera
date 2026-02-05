# Environment Variables Setup Guide

This guide walks you through setting up all required environment variables for Project Chimera.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in your actual values** (see sections below)

3. **Validate your setup:**
   ```bash
   python scripts/validate_env.py
   ```

---

## Required Services

### 1. Redis (Required)

**Purpose**: Queue management for TaskQueue and ReviewQueue

**Setup Options:**

#### Option A: Local Redis (Development)
```bash
# Install Redis
# macOS:
brew install redis
brew services start redis

# Ubuntu/Debian:
sudo apt-get install redis-server
sudo systemctl start redis-server

# Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

**Environment Variables:**
```bash
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### Option B: Redis Cloud (Production)
1. Sign up at [Redis Cloud](https://redis.com/try-free/)
2. Create a database
3. Copy the connection URL:
```bash
REDIS_URL=redis://default:password@your-redis-host:port
```

**Validation:**
```bash
redis-cli ping
# Should return: PONG
```

---

### 2. Weaviate (Required)

**Purpose**: Vector database for semantic memory (RAG pipeline)

**Setup Options:**

#### Option A: Local Weaviate (Development)
```bash
# Using Docker Compose (recommended)
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -p 50051:50051 \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  -e ENABLE_MODULES=text2vec-openai \
  -e CLUSTER_HOST=127.0.0.1 \
  semitechnologies/weaviate:latest
```

**Environment Variables:**
```bash
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=  # Leave empty for local dev
```

#### Option B: Weaviate Cloud (Production)
1. Sign up at [Weaviate Cloud](https://console.weaviate.cloud/)
2. Create a cluster
3. Get your API key and URL:
```bash
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-api-key-here
```

**Validation:**
```bash
curl http://localhost:8080/v1/meta
# Should return cluster metadata
```

---

### 3. Coinbase Developer Platform (Required for Commerce)

**Purpose**: Non-custodial wallet management via AgentKit

**Setup Steps:**

1. **Create a Coinbase Developer Account:**
   - Go to [Coinbase Developer Portal](https://portal.cdp.coinbase.com/)
   - Sign in with your Coinbase account

2. **Create an API Key:**
   - Navigate to "API Keys" section
   - Click "Create API Key"
   - Name it (e.g., "chimera-agent-wallet")
   - Select permissions: `Wallet:Read`, `Wallet:Write`
   - Copy the **API Key Name** (not the key itself)

3. **Generate Private Key:**
   - In the API key details, click "Generate Private Key"
   - **IMPORTANT**: Save this immediately - you can only see it once!
   - Copy the entire private key (including BEGIN/END markers)

4. **Set Environment Variables:**
```bash
CDP_API_KEY_NAME=your-api-key-name-from-step-2
CDP_API_KEY_PRIVATE_KEY="-----BEGIN EC PRIVATE KEY-----
...your private key here...
-----END EC PRIVATE KEY-----"
```

**Security Note:**
- Never commit these keys to git
- Use secrets management in production (AWS Secrets Manager, HashiCorp Vault)
- Rotate keys regularly

**Validation:**
```python
# Test script
from chimera.core.commerce import CommerceManager
import asyncio

async def test():
    manager = CommerceManager()
    balance = await manager.get_balance("USDC")
    print(f"Wallet Balance: {balance} USDC")
    print(f"Wallet Address: {manager.get_wallet_address()}")

asyncio.run(test())
```

---

## Optional Services

### 4. PostgreSQL (Optional - for persistent storage)

**Purpose**: Structured data storage (campaigns, tasks, transactions)

**Setup:**
```bash
# Local PostgreSQL
# macOS:
brew install postgresql
brew services start postgresql

# Ubuntu/Debian:
sudo apt-get install postgresql
sudo systemctl start postgresql

# Create database
createdb chimera_db
```

**Environment Variables:**
```bash
POSTGRES_URL=postgresql://chimera:chimera_password@localhost:5432/chimera_db
```

**Initialize Schema:**
```python
from chimera.core.database import POSTGRES_SCHEMA
# Run POSTGRES_SCHEMA SQL in your database
```

---

### 5. LLM API Keys (Optional - for future features)

#### Gemini API (Google)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create API key
3. Set: `GEMINI_API_KEY=your-key`

#### Anthropic Claude
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create API key
3. Set: `ANTHROPIC_API_KEY=your-key`

#### OpenAI
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create API key
3. Set: `OPENAI_API_KEY=your-key`

---

## Environment-Specific Configuration

### Development
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
NUM_WORKERS=2
MAX_DAILY_USDC=10.0  # Lower limit for testing
```

### Production
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
NUM_WORKERS=10
MAX_DAILY_USDC=1000.0
```

---

## Validation Script

Run the validation script to check your setup:

```bash
python scripts/validate_env.py
```

This will check:
- ✅ All required variables are set
- ✅ Redis connection works
- ✅ Weaviate connection works
- ✅ Coinbase credentials are valid (if provided)
- ⚠️ Warns about missing optional variables

---

## Troubleshooting

### Redis Connection Failed
```bash
# Check if Redis is running
redis-cli ping

# Check connection string format
# Correct: redis://localhost:6379/0
# Wrong: redis://localhost:6379 (missing database number)
```

### Weaviate Connection Failed
```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/meta

# For Docker, check logs
docker logs weaviate
```

### Coinbase API Errors
- Verify API key name matches exactly (case-sensitive)
- Ensure private key includes BEGIN/END markers
- Check API key permissions (Wallet:Read, Wallet:Write)
- Verify you're using Base network (not Ethereum mainnet)

### Environment Variables Not Loading
- Ensure `.env` file is in project root
- Check for typos in variable names
- Restart your Python process/IDE after changing `.env`
- Use `python-dotenv` to load: `from dotenv import load_dotenv; load_dotenv()`

---

## Security Best Practices

1. **Never commit `.env` to git** (already in `.gitignore`)
2. **Use `.env.example`** for documentation
3. **Rotate secrets regularly** (especially Coinbase keys)
4. **Use secrets management in production:**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Kubernetes Secrets
5. **Limit API key permissions** (principle of least privilege)
6. **Monitor API usage** for unexpected activity

---

## Next Steps

After setting up environment variables:

1. **Validate setup:** `python scripts/validate_env.py`
2. **Run tests:** `make test`
3. **Start services:** `docker-compose up` (if using Docker)
4. **Initialize database:** Run PostgreSQL schema migration
5. **Test MCP servers:** Start individual MCP servers

For more details, see `README.md` and `IMPLEMENTATION_STATUS.md`.

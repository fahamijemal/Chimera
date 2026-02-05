# Environment Variables Quick Reference

## Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `WEAVIATE_URL` | Weaviate instance URL | `http://localhost:8080` |

## Optional (But Recommended)

| Variable | Description | Example |
|----------|-------------|---------|
| `CDP_API_KEY_NAME` | Coinbase CDP API key name | `chimera-wallet-key` |
| `CDP_API_KEY_PRIVATE_KEY` | Coinbase CDP private key | `-----BEGIN EC PRIVATE KEY-----...` |
| `WEAVIATE_API_KEY` | Weaviate API key (if authenticated) | `your-api-key` |

## Budget Limits

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_DAILY_USDC` | Max daily USDC spending | `50.0` |
| `MAX_DAILY_ETH` | Max daily ETH spending | `0.01` |

## LLM API Keys (Future)

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `GEMINI_API_KEY` | Google Gemini API key | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | [Anthropic Console](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | OpenAI API key | [OpenAI Platform](https://platform.openai.com/api-keys) |

## Application Config

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `NUM_WORKERS` | Number of worker agents | `3` |
| `DEFAULT_RELEVANCE_THRESHOLD` | Semantic filter threshold | `0.75` |

## Quick Setup

```bash
# 1. Copy template
cp .env.example .env

# 2. Edit .env with your values
nano .env  # or use your preferred editor

# 3. Validate
python scripts/validate_env.py
```

## Service URLs

### Local Development
- Redis: `redis://localhost:6379/0`
- Weaviate: `http://localhost:8080`
- PostgreSQL: `postgresql://chimera:password@localhost:5432/chimera_db`

### Production
- Use cloud-hosted services
- Store credentials in secrets management
- Never commit `.env` to git

## See Also

- **[ENV_SETUP.md](ENV_SETUP.md)**: Detailed setup guide
- **[scripts/validate_env.py](scripts/validate_env.py)**: Validation script

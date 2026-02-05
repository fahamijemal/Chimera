# Project Chimera: Autonomous Influencer Network

**Agentic Infrastructure for Building Autonomous AI Influencers**

Project Chimera is a sophisticated multi-agent system that creates and manages autonomous digital influencers capable of perception, reasoning, creative expression, and economic agency.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (for queue management)
- Weaviate (for semantic memory)
- Coinbase Developer Platform account (for agentic commerce)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd chimera
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Install dependencies:**
   ```bash
   make setup
   # or
   uv pip install -e ".[dev]"
   ```

4. **Validate your setup:**
   ```bash
   python scripts/validate_env.py
   ```

5. **Run tests:**
   ```bash
   make test
   ```

## 📋 Environment Setup

**See [ENV_SETUP.md](ENV_SETUP.md) for detailed instructions.**

Quick checklist:
- ✅ Redis running (local or cloud)
- ✅ Weaviate running (local or cloud)
- ✅ Coinbase CDP API keys configured
- ✅ Environment variables set in `.env`

## 🏗️ Architecture

Project Chimera uses the **FastRender Swarm** pattern:

- **Planner**: Decomposes goals into tasks
- **Worker**: Executes tasks using MCP tools
- **Judge**: Validates outputs and routes via HITL
- **Orchestrator**: Manages swarm lifecycle

All external interactions use **Model Context Protocol (MCP)** for standardization.

## 📁 Project Structure

```
chimera/
├── specs/              # Source of Truth (SRS)
│   ├── functional.md   # User stories & workflows
│   ├── technical.md    # API contracts & schemas
│   └── _meta.md        # Vision & constraints
├── research/           # Architecture & strategy docs
├── skills/             # Agent Skill definitions
├── chimera/            # Source code
│   ├── core/           # State, queues, memory, commerce
│   ├── agents/         # Planner, Worker, Judge
│   └── mcp/            # MCP clients & servers
├── tests/              # Test suite (TDD)
├── personas/           # SOUL.md agent definitions
├── scripts/            # Utility scripts
├── Dockerfile          # Containerization
├── Makefile            # Standardized commands
└── .env.example        # Environment template
```

## 🛠️ Development

### Make Commands

```bash
make setup      # Install dependencies
make test       # Run test suite
make lint       # Run linters (ruff, black)
make build      # Build Docker image
make shell      # Enter development shell
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_core_agents.py

# Run with coverage
pytest --cov=chimera
```

### Starting Services

**Redis:**
```bash
# Local
redis-server

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

**Weaviate:**
```bash
# Docker
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  semitechnologies/weaviate:latest
```

## 📚 Documentation

- **[ENV_SETUP.md](ENV_SETUP.md)**: Environment configuration guide
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)**: Implementation status
- **[specs/](specs/)**: Complete specifications
- **[research/](research/)**: Architecture and tooling strategies

## 🔐 Security

- Never commit `.env` to git (already in `.gitignore`)
- Use secrets management in production
- Rotate API keys regularly
- Follow principle of least privilege for API permissions

## 🧪 Testing

Project Chimera follows **Test-Driven Development (TDD)**:

1. Write failing tests first
2. Implement to pass tests
3. Refactor

Test coverage includes:
- Core agent logic (Planner, Worker, Judge)
- State management (OCC)
- Persona system
- MCP integration
- Trend detection

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t chimera .

# Run container
docker run --env-file .env chimera
```

### CI/CD

GitHub Actions workflow runs on every push:
- Runs test suite
- Checks code quality
- Validates spec alignment (via CodeRabbit)

## 🤝 Contributing

1. Read `specs/` before implementing features
2. Follow TDD approach
3. Ensure all tests pass
4. Update documentation

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- FastRender Swarm pattern inspiration
- Model Context Protocol (MCP) standard
- Coinbase AgentKit for agentic commerce

---

**Status**: ✅ Core Infrastructure Complete - Ready for feature development

For questions or issues, see `ENV_SETUP.md` or check `IMPLEMENTATION_STATUS.md`.

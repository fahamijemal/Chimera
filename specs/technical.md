# Technical Specification

## 1. Directory Structure
```
chimera/
├── specs/              # Source of Truth
├── research/           # Strategy docs
├── skills/             # Agent Skill Definitions
├── chimera/            # Source Code
│   ├── core/           # Orchestrator, State
│   ├── agents/         # Planner, Worker, Judge logic
│   ├── memory/         # Weaviate/Redis wrappers
│   └── mcp/            # MCP Client & Server config
├── tests/              # TDD
├── Dockerfile
├── Makefile
└── pyproject.toml
```

## 2. API Contracts & Schemas

### Agent Task (JSON)
```json
{
  "task_id": "uuid-v4",
  "task_type": "generate_content | social_action | transaction",
  "priority": "high | medium | low",
  "context": {
    "goal": "string",
    "persona_constraints": ["string"],
    "resources": ["mcp://uri"]
  },
  "assigned_worker_id": "string",
  "status": "pending | processing | review | complete"
}
```

### MC Tool Definition (Example: Post)
```json
{
  "name": "post_content",
  "inputSchema": {
    "type": "object",
    "properties": {
      "platform": {"enum": ["twitter", "instagram"]},
      "content": {"type": "string"},
      "media_urls": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["platform", "content"]
  }
}
```

## 3. Database Schema (ERD)

### PostgreSQL (Structural)
- **`campaigns`**: `id`, `goal_description`, `status`, `budget_limit`
- **`tasks`**: `id`, `campaign_id`, `worker_type`, `status`, `result_artifact`
- **`transactions`**: `id`, `wallet_address`, `amount`, `currency`, `tx_hash`

### Weaviate (Semantic)
- **`Memory`**: `content` (text), `vector`, `timestamp`, `importance_score`
- **`Persona`**: `name`, `voice_traits`, `biography_embedding`

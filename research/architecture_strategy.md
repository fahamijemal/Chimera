# Domain Architecture Strategy

## 1. Agent Pattern: FastRender Swarm
Project Chimera adopts the **FastRender Swarm** architecture to manage autonomous behavior. This is not a single agent but a hierarchical system of specialized roles.

### Roles
- **Planner (The Strategist)**:
    - **Responsibility**: Maintains `GlobalState`, decomposes high-level goals into tasks, and manages the DAG of operations.
    - **Behavior**: Reactive to "Trend Alerts" and context shifts. Spawns Sub-Planners for complex campaigns.
    - **Persistence**: Stateful (Long-running).

- **Worker (The Executor)**:
    - **Responsibility**: Executes atomic tasks (e.g., "Generate Image", "Draft Tweet") using MCP Tools.
    - **Behavior**: Stateless and ephemeral. Scalable horizontally (1..N).
    - **Constraint**: Shared-nothing architecture.

- **Judge (The Gatekeeper)**:
    - **Responsibility**: QA layer. validating Worker outputs against Persona/Safety constraints.
    - **Authority**: Approve (commit), Reject (retry), or Escalate (HITL).
    - **Mechanism**: Uses Optimistic Concurrency Control (OCC) to prevent race conditions during state updates.

## 2. Human-in-the-Loop (HITL) Strategy
We implement a "Management by Exception" model using confidence scoring.

### Confidence Tiers
- **> 0.90 (High)**: **Auto-Approve**. Action executes immediately.
- **0.70 - 0.90 (Medium)**: **Async Approval**. Queued for human review. Agent proceeds with other tasks.
- **< 0.70 (Low)**: **Reject/Retry**. Automatic rejection; Planner must re-strategize.

### The "CFO" Judge
- Specialized Judge Agent for financial transactions.
- Strictly enforces budget limits (e.g., Max Daily Spend).
- Any transaction > Limit is REJECTED or FLAGGED.

## 3. Data Persistence Strategy
The architecture uses a polyglot persistence layer to handle different data modalities.

- **Semantic Memory (Long-Term)**: **Weaviate**
    - Stores: Agent Personas (`SOUL.md` embeddings), Memories, World Knowledge.
    - Usage: RAG pipeline retrieves relevant context for every interaction.

- **Transactional Data (State)**: **PostgreSQL**
    - Stores: User Accounts (Multi-tenancy), Campaign Configs, Financial Ledger (`ProjectChimera` tables).
    - Usage: Structural integrity and relational data.

- **Episodic & Queues (Short-Term)**: **Redis**
    - Stores: Task Queues (`planner_queue`, `review_queue`), Short-term conversational context (1-hour window).
    - Usage: High-speed state management for the Swarm.

- **Ledger (Financial)**: **Blockchain (Base/CBP)**
    - Usage: Immutable record of financial transactions via Coinbase AgentKit.

## 4. Integration Topology: MCP Hub-and-Spoke
- **Hub**: Central Orchestrator (Agent Swarm Runtime).
- **Spokes**: MCP Servers providing capabilities.
    - `mcp-server-social` (Twitter/Instagram)
    - `mcp-server-memory` (Weaviate)
    - `mcp-server-wallet` (Coinbase)
- **Benefit**: Decouples Agent Logic from API implementations.

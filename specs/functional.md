# Functional Specification

## 1. User Stories

### Network Operator (The Human)
- **Goal Setting**: "As an Operator, I want to set a high-level campaign goal (e.g., 'Promote Summer Line') so the Planner can decompose it."
- **Monitoring**: "As an Operator, I want to see a live dashboard of Agent States (Planning, Working, Judging) and Wallet Balances."
- **Review**: "As an Operator, I want to approve/reject 'Medium Confidence' content in a queue."

### The Planner (Agent Role)
- **Decomposition**: "As a Planner, I need to break a 'Goal' into atomic 'Tasks' based on available Resources."
- **Reaction**: "As a Planner, I need to listen to 'Trend Alerts' to pivot my strategy."

### The Worker (Agent Role)
- **Execution**: "As a Worker, I need to execute tools (e.g., `generate_image`, `post_tweet`) without knowing the underlying API details."
- **Isolation**: "As a Worker, I must share NO state with other workers."

### The Judge (Agent Role)
- **Validation**: "As a Judge, I need to verify that a generated image matches the `character_reference_id`."
- **Budgeting**: "As a 'CFO' Judge, I must REJECT any transaction that exceeds the daily spending limit."

## 2. Workflows

### The Perception-Action Loop
1. **Ingest**: Planner receives `news://update` or `social://mention`.
2. **Filter**: Semantic Filter checks relevance (>0.75).
3. **Plan**: Planner creates `Task` -> `TaskQueue`.
4. **Work**: Worker picks `Task`, calls MCP Tool, produces `Result`.
5. **Judge**: Judge picks `Result`, validates (Auto/HITL), commits to `GlobalState`.

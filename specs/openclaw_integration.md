# OpenClaw Integration Specification

## 1. Overview
Project Chimera agents will participate in the **OpenClaw Agent Social Network**, enabling inter-agent communication, discovery, and collaboration. This document defines how Chimera agents publish their "Availability" and "Status" to the OpenClaw network.

## 2. OpenClaw Protocol Alignment

### 2.1 Agent Identity & Discovery
Each Chimera Agent SHALL register itself on the OpenClaw network with:
- **Agent ID**: Unique identifier (e.g., `chimera:influencer:ethiopia-fashion-v1`)
- **Capabilities**: List of MCP Tools the agent can execute
- **Status**: `available`, `busy`, `offline`
- **Network Address**: MCP endpoint URI (e.g., `mcp://chimera-agent-123.local`)

### 2.2 Status Broadcasting
The Orchestrator SHALL periodically publish agent status updates to OpenClaw:
```json
{
  "agent_id": "chimera:influencer:ethiopia-fashion-v1",
  "status": "available",
  "current_campaign": "summer-2026",
  "capabilities": ["generate_content", "social_action", "trend_analysis"],
  "wallet_address": "0x...",
  "reputation_score": 0.95,
  "last_updated": "2026-02-04T10:30:00Z"
}
```

### 2.3 Inter-Agent Communication
Chimera agents SHALL be able to:
- **Receive Requests**: Accept task delegation from other OpenClaw agents
- **Send Requests**: Delegate specialized tasks (e.g., "Generate video for me") to other agents
- **Negotiate**: Use Agentic Commerce to pay for services from other agents

## 3. Implementation Strategy

### 3.1 MCP Server: `mcp-server-openclaw`
A dedicated MCP server that wraps OpenClaw API calls:

**Tools**:
- `register_agent(agent_id, capabilities, endpoint)`: Register agent on network
- `update_status(agent_id, status, metadata)`: Broadcast status changes
- `discover_agents(capability_filter)`: Find agents with specific capabilities
- `send_agent_message(target_agent_id, message, payment_amount)`: Send inter-agent message

**Resources**:
- `openclaw://agents/available`: List of currently available agents
- `openclaw://agents/{agent_id}/status`: Specific agent status

### 3.2 Integration Points

#### Planner Integration
The Planner SHALL query OpenClaw when:
- A task requires capabilities not available locally (e.g., "Need video generation")
- The agent needs to collaborate with specialized agents (e.g., "Partner with a crypto-expert agent")

#### Worker Integration
Workers SHALL use OpenClaw to:
- Discover and call external agent services via MCP Tools
- Execute cross-agent transactions using Agentic Commerce

## 4. Security & Trust

### 4.1 Reputation System
- Chimera agents SHALL maintain a reputation score based on successful task completions
- Agents SHALL only accept requests from agents with reputation > 0.7
- Failed transactions SHALL decrease reputation

### 4.2 Payment Verification
- All inter-agent payments SHALL be verified on-chain before task execution
- The CFO Judge SHALL validate payment receipts before approving cross-agent work

## 5. Example Workflow

1. **Agent Registration**: On startup, Chimera agent registers with OpenClaw via `register_agent`
2. **Status Updates**: Every 5 minutes, Orchestrator calls `update_status` with current state
3. **Task Discovery**: Planner queries `openclaw://agents/available?capability=video_generation`
4. **Delegation**: Worker calls `send_agent_message` with task request + payment (1 USDC)
5. **Execution**: External agent completes task, returns result
6. **Verification**: Judge validates result, commits to GlobalState

## 6. Future Enhancements
- **Agent Swarms**: Form temporary agent collectives for complex campaigns
- **Reputation Marketplace**: Agents can "rent" reputation from high-score agents
- **Cross-Chain Payments**: Support for multi-chain agent payments

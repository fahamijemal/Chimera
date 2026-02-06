# Security Specification

## 1. Authentication & Authorization (AuthN/AuthZ)

### Strategy
Project Chimera uses a **Zero-Trust** approach for all inter-agent and external communication.

*   **Internal (Agent-to-Agent):** No direct interaction. All state changes mediated by the `Orchestrator` via `GlobalState`.
*   **External (MCP Tools):** All MCP servers run in isolated subprocesses.
*   **API Keys:** Managed via `.env` file, NOT stored in code.

### Secrets Management
*   **Storage:** Local `.env` file (gitignored). In production, AWS Secrets Manager.
*   **Injection:** Environment variables injected into Docker container at runtime.
*   **Rotation:** Keys (Google Gemini, Coinbase CDP) must be rotated every 30 days.

---

## 2. Agent Containment Boundaries

To prevent "Runaway Agent" scenarios, the following hard limits are enforced by the `Orchestrator`:

### Resource Limits
*   **Memory:** Max 512MB per Worker Agent (Enforced via Docker `mem_limit`).
*   **CPU:** Max 0.5 vCPU per Worker.
*   **Recursion:** Max `sub-task` depth = 3.

### Forbidden Actions (The "Red List")
The following tools/actions are **HARD BLOCKED** at the SkillExecutor level:
1.  **Shell Access:** No usage of `subprocess.run` with `shell=True` outside of specific, whitelisted MCP servers.
2.  **File System:**
    *   **Allowed:** Read/Write to `./data/artifacts/`.
    *   **Forbidden:** Write access to root `/`, `/etc`, or source code directories `chimera/`.
3.  **Network:**
    *   **Allowed:** Whitelisted domains (google.com, twitter.com, coinbase.com).
    *   **Forbidden:** LAN scanning or connection to internal IPs (192.168.x.x).

---

## 3. Input/Output Guardrails

### Content Safety (Judge Agent)
*   **Trigger:** Every `generate_content` output.
*   **Mechanism:** Google Gemini Safety Filter.
*   **Threshold:** Block any content with `HARM_CATEGORY_SEXUALLY_EXPLICIT` or `HARM_CATEGORY_HATE_SPEECH` > `BLOCK_MEDIUM_AND_ABOVE`.

### Economic Safety (CFO Persona)
*   **Trigger:** Every `transaction` task.
*   **Mechanism:** Pre-flight check against `GlobalState.daily_spend`.
*   **Rule:** `IF (current_daily_spend + tx_amount) > MAX_DAILY_USDC THEN REJECT`.

---

## 4. Human-in-the-Loop (HITL)

### Escalation Triggers
The system MUST pause and request human generic approval if:
1.  **Confidence Score** < 0.7.
2.  **Transaction Amount** > $10.00.
3.  **Sentiment Analysis** detects "Hostile" user feedback.

### Override Mechanism
*   Operator can issue `SIGINT` (Ctrl+C) to hard-stop the swarm.
*   Operator can inject `OverrideInstruction` via the Dashboard.

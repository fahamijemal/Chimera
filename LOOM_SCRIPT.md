# Loom Video Submission Script (Max 5 Minutes)

## 0. Setup (Before Recording)
- Open VS Code / Cursor.
- Terminal 1: Run `make test` (Show it passing).
- Terminal 2: Run `demo_swarm.py` (optional, or just show the code).
- Open `specs/technical.md` and `chimera/agents/planner.py`.
- Ensure **Tenx MCP** is connected (Green light in Cursor/VSCode).

## 1. Introduction (30s)
*   "Hi, I'm [Your Name]. This is my Day 1 & 2 submission for Project Chimera."
*   "I have built the 'Golden Environment' using **Spec-Driven Development** and the **FastRender Swarm** architecture."
*   "The tech stack is Python 3.12, Pydantic, Weaviate, and the **official MCP SDK** for integration."

## 2. Spec-Driven Architecture (1m)
*   *Navigate to `specs/` folder.*
*   "Everything starts with the specs. Here is `technical.md` defining the Data Models and API contracts."
*   "I used these specs to drive the codebase. For example, the `Task` model in `specs/technical.md` maps directly to `chimera/core/models.py`."
*   *Briefly show `chimera/core/models.py`.*

## 3. TDD Proof (1m)
*   "Following the Governor's rules, I used TDD."
*   *Run `make test` in the terminal.*
*   "As you can see, `test_trend_fetcher` and `test_skills_interface` are PASSING."
*   "I also implemented a **Real MCP Integration test** (`test_mcp_integration.py`) that spawns a real `FastMCP` server process and queries it via the client."

## 4. The Swarm Logic (1m 30s)
*   *Open `chimera/agents/planner.py`.*
*   "I implemented the FastRender pattern."
*   "The **Planner** decomposes goals."
*   "The **Worker** executes tools via the MCP Client."
*   "The **Judge** validates results."
*   "This separation enables the swarm to self-correct."

## 5. IDE Context & Tenx MCP (1m)
*   *Open `.cursor/rules/project_rules.mdc`.*
*   "I configured my IDE with strict context rules."
*   *Open the Chat Panel.*
*   *Ask the Agent:* "Explain the role of the Judge in this project."
*   *(Show that it answers using your specific rules).*
*   "Finally, as you can see, the **Tenx MCP Sense** server is active and logging telemetry."

## 6. Closing
*   "The repository is ready for scaling. Thank you."

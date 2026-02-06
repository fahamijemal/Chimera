# Frontend Specification: Operator Dashboard

## 1. Component Hierarchy & Data Binding

This document maps the User Interface components to the backend API contracts defined in `specs/technical.md`.

### A. Dashboard Layout (`/dashboard`)

| Component | Purpose | Backend Source (API) | Data Schema |
| :--- | :--- | :--- | :--- |
| **SwarmStatusWidget** | Shows active agents | `GET /api/swarm/status` | `{ "active_workers": int, "queue_depth": int }` |
| **GoalInputForm** | Operator sets new goal | `POST /api/goals` | `{ "goal_description": string, "priority": enum }` |
| **ActivityFeed** | Live log of actions | `WS /ws/events` | `Stream[LogEvent]` |
| **WalletWidget** | Shows USDC balance | `GET /api/commerce/balance` | `{ "total_usdc": float, "daily_spend": float }` |

---

## 2. Interaction Flows

### Flow: Reviewing Content
**User Story:** "As an Operator, I want to approve generated images."

1.  **UI Event:** User clicks "Review Queue" tab.
2.  **API Call:** `GET /api/tasks?status=review`.
3.  **Response:** List of `Task` objects (see `technical.md` Task Schema).
4.  **UI Component:** `ReviewCard` renders `task.result_artifact.image_url`.
5.  **User Action:** Clicks "Approve".
6.  **API Call:** `POST /api/tasks/{id}/approve`.
7.  **Backend Logic:** Judge Agent commits the image to social queue.

### Flow: Emergency Stop
**User Story:** "As an Operator, I want to halt a runaway agent."

1.  **UI Event:** User clicks **"EMERGENCY STOP"** (Red Button).
2.  **API Call:** `POST /api/admin/kill-switch`.
3.  **Backend Logic:**
    *   Orchestrator sends `SIGTERM` to all Worker containers.
    *   Flushes `TaskQueue` to empty.
    *   Resets `GlobalState` to "PAUSED".

---

## 3. Design System (Tokens)

*   **Typography:** Terminus (Monospace) for logs; Inter for UI text.
*   **Colors:**
    *   `Status: Active` -> `#00FF00` (Cyber Green)
    *   `Status: Error` -> `#FF0000` (Alert Red)
    *   `Background` -> `#0A0A0A` (Deep Space)
*   **Accessibility:** All form inputs must have `aria-label` matching the API field name.

# Acceptance Criteria

This document defines the formal conditions for when Project Chimera features are considered "Done". 
Language: **Gherkin (Given/When/Then)** for autonomous test generation compatibility.

## 1. Core Agent Logic (The Brain)

### Feature: Goal Decomposition
**User Story:** As a Planner, I want to break high-level goals into atomic tasks.

```gherkin
Scenario: Breakdown of a broad marketing goal
  Given the Planner Agent is initialized with `gemini-pro`
  And the current context includes "Active Campaign: Summer Launch"
  When the Planner receives the goal "Promote our new eco-friendly sneakers on Twitter"
  Then it should produce a "Task Plan" containing at least 2 steps:
    | Task Type      | Context Keyword |
    | social_action  | tweet           |
    | generate_image | sneakers        |
  And the `confidence_score` of the plan should be > 0.8
```

### Feature: Trend Perception
**User Story:** As a Planner, I want to fetch news to inform my strategy.

```gherkin
Scenario: Fetching relevant tech trends
  Given the MCP News Server is running at `localhost:8000`
  When the Planner executes the `fetch_trends` skill with category "AI"
  Then the result should contain a list of at least 3 active headlines
  And the result metadata should include a "timestamp" within the last 24 hours
  And if the RSS feed is down, it should return a "Mock/Fallback" result without crashing
```

---

## 2. Worker Execution (The Hands)

### Feature: Tool Selection
**User Story:** As a Worker, I want to select the right tool for a task.

```gherkin
Scenario: Choosing Image Generation for Visual Tasks
  Given a Task with `task_type="generate_content"`
  And the available MCP tools include `["generate_image", "post_tweet", "send_email"]`
  When the Worker analyzes the task prompt "Create a cyberpunk city image"
  Then it should select the tool `generate_image`
  And the argument `prompt` should contain "cyberpunk city"
```

### Feature: State Isolation
**User Story:** As a Worker, I must be stateless.

```gherkin
Scenario: Worker Cleanup after Task
  Given a Worker `Worker-A` has completed `Task-123`
  When `Task-124` is assigned to `Worker-A`
  Then `Worker-A` should have NO memory of `Task-123` artifacts
  And the internal `context_window` should be reset
```

---

## 3. Governance (The Judge)

### Feature: Budget Enforcement
**User Story:** As a Judge, I must reject expensive actions.

```gherkin
Scenario: Rejecting Over-Budget Transactions
  Given the Global State shows `daily_spend_usdc = 45.0`
  And the `MAX_DAILY_USDC` is `50.0`
  When a Worker proposes a transaction of `10.0 USDC`
  Then the Judge should return `status="rejected"`
  And the rejection reason should contain "Budget Limit Exceeded"
```

### Feature: Safety Rails
**User Story:** As a Judge, I must filter unsafe content.

```gherkin
Scenario: Filtering NSWF Content
  Given a generated image result
  When the Safety Classifier detects "Explicit Content" (probability > 0.9)
  Then the Judge should mark the task as `failed`
  And an alert should be logged to `admin_queue`
```

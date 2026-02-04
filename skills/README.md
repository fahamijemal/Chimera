# Agent Skills Directory

This directory contains the "Skills" (Runtime capabilities) exposed to the Chimera Agents via MCP.

## Skill Categories

### 1. Perception (`skill_perception`)
- **Purpose**: Ingest real-world data.
- **Resources**:
    - `news://latest?topic={topic}`
    - `social://mentions`
    - `market://price/{symbol}`

### 2. Action (`skill_social_action`)
- **Purpose**: Interact with social platforms.
- **Tools**:
    - `post_tweet(content: str, media_urls: List[str])`
    - `reply_to_comment(comment_id: str, content: str)`

### 3. Creation (`skill_content_gen`)
- **Purpose**: Generate assets.
- **Tools**:
    - `generate_image(prompt: str, aspect_ratio: str, character_id: str)`
    - `generate_text(prompt: str, context: str)`

## Interface Contract
All skills must handle errors gracefully and return standardized JSON artifacts.

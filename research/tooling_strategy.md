# Tooling & Skills Strategy

## 1. Developer Tools (MCP)
Tools used by the **Forward Deployed Engineer** to build the system.

- **Filesystem MCP**: Reading/Writing code and specs.
- **Git MCP**: Version control operations.
- **Terminal/Command MCP**: Running tests and build commands.
- **Tenx MCP Sense**: "Black box" flight recorder for traceability.

## 2. Agent Skills (Runtime)
Capabilities exposed to the **Worker Agents** via MCP.

### Core Skills
- **`skill_perception`**:
    - **Resource**: `news://*`, `social://mentions/*`
    - **Action**: Fetch latest trends, read mentions.
- **`skill_social_action`**:
    - **Tool**: `post_tweet`, `reply_thread`, `dm_user`
    - **Safety**: Rate-limited, logging-enabled wrapper around social APIs.
- **`skill_content_gen`**:
    - **Tool**: `generate_image`, `generate_text`, `render_video`
    - **Constraint**: Must accept `character_reference_id` for consistency.
- **`skill_wallet`**:
    - **Tool**: `transfer_asset`, `get_balance`
    - **Security**: Requires "CFO" Judge approval.

## 3. Tooling Logic
- **Architecture**: Tools are essentially MCP Server Functions.
- **Discovery**: Agents discover tools via the MCP `list_tools` capability on startup.
- **Validation**: All tool inputs are validated against Pydantic schemas before execution.

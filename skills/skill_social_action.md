# Skill: Social Action

## 1. Description
Allows the agent to interact with social media platforms (Twitter, Instagram, etc) via a unified interface.

## 2. Input Contract: `post_content`
| Field | Type | Description |
|-------|------|-------------|
| `content` | `string` | The text content to post. |
| `media_urls` | `list[string]` | Optional list of image/video URLs. |

## 3. Input Contract: `reply_to_comment`
| Field | Type | Description |
|-------|------|-------------|
| `comment_id` | `string` | ID of the target comment. |
| `text` | `string` | The reply text. |

## 4. Implementation Details
- Uses **MCP Tools** provided by `mcp-server-social` (or simulated).
- Validates content length and safety policies before execution.

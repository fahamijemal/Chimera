# Skill: Fetch Trends

## 1. Description
Retrieves latest industry trends and news headlines from configured Perception servers.

## 2. Input Contract
| Field | Type | Description |
|-------|------|-------------|
| `category` | `string` | Optional filter (e.g., "tech", "finance"). |
| `limit` | `integer` | Number of headlines to return (default 5). |

## 3. Output Contract
| Field | Type | Description |
|-------|------|-------------|
| `headlines` | `list[object]` | List of objects containing `title`, `source`, `link`. |
| `timestamp` | `string` | ISO format. |

## 4. Implementation Details
- Connects to `chimera/mcp/servers/news_server.py` via MCP.
- Parses RSS feeds using `feedparser`.

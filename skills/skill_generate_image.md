# Skill: Generate Image

## 1. Description
Generates a high-quality AI image based on a text prompt to be used in social media posts.

## 2. Input Contract
| Field | Type | Description |
|-------|------|-------------|
| `prompt` | `string` | The detailed description of the image to generate. |
| `character_id` | `string` | The ID of the persona to maintain visual consistency. |

## 3. Output Contract
| Field | Type | Description |
|-------|------|-------------|
| `status` | `string` | "success" or "error" |
| `url` | `string` | Publicly accessible URL for the image. |
| `local_path` | `string` | Absolute server path to the file. |
| `metadata` | `object` | Generation parameters (model, seed, etc). |

## 4. Implementation Details
- Uses **Google Imagen 3/4** via `google-genai` SDK.
- Support for **Mock Fallback**: If API is unavailable, generates a local grayscale placeholder to prevent blocking.

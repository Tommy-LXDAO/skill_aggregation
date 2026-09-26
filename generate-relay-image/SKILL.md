---
name: generate-relay-image
description: Generate raster images with the gpt-image-2 model by resolving the active provider, Base URL, and Codex authentication from ~/.codex/config.toml and ~/.codex/auth.json, then save decoded files locally. Use when the user asks to generate, draw, create, or render an image through their current Codex provider rather than through a repository-specific service or Codex's built-in image tool.
---

# Generate Image From Codex Config

Use `scripts/generate_image.py` for the request and file handling.

## Configuration contract

Resolve configuration independently of every workspace and repository:

1. Read the active provider name from `model_provider` in `~/.codex/config.toml`.
2. Read its `base_url` from `model_providers.<name>`.
3. If the provider declares an API-key environment field, read that environment variable.
4. When `requires_openai_auth = true`, read `OPENAI_API_KEY` from the process environment, then fall back to `~/.codex/auth.json`.
5. Always use model `gpt-image-2` and append `/images/generations` to the configured Base URL.

Never read a project `.env` file. Never print, copy, or write the API key into skill files, commands, logs, output metadata, or generated files.

Use these defaults unless the user requests otherwise:

- Size: `1024x1024`
- Quality: `high`
- Output format: `png`
- Moderation: `low`
- Timeout: 1200 seconds

## Workflow

1. Turn the user's visual request into one self-contained generation prompt. Preserve requested text exactly and specify composition, subject, lighting, palette, style, aspect ratio, and exclusions only when useful.
2. Ask for clarification only when a missing choice would materially change the image. Otherwise make a reasonable visual choice.
3. Run the script with an absolute output path:

```bash
python3 scripts/generate_image.py \
  --prompt "A precise, self-contained image prompt" \
  --output /absolute/path/generated-image.png
```

4. Use `--size`, `--quality`, `--n`, or `--output-format` only when needed. Use `--dry-run` to verify the resolved provider and request without spending image-generation credits.
5. Verify that every reported output exists and is non-empty. Inspect the image when visual quality matters and iterate once with a targeted prompt change.
6. Return clickable absolute file links and render the final image when the client supports it.

## Failure handling

- Stop on missing or ambiguous provider configuration; do not guess a provider, Base URL, or credential.
- Treat HTTP 401/403 as an authentication/configuration problem; do not retry with guessed credentials.
- Treat HTTP 429 and 5xx as upstream failures. Retry at most once when appropriate, then report the status and sanitized error body.
- Do not silently switch providers, models, Base URLs, or authentication sources.
- If the response contains neither `b64_json` nor `url`, stop and report the response-shape mismatch.

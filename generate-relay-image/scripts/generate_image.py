#!/usr/bin/env python3
"""Generate images using the active provider in ~/.codex/config.toml."""

from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MODEL = "gpt-image-2"
CONFIG_PATH = Path.home() / ".codex" / "config.toml"
AUTH_PATH = Path.home() / ".codex" / "auth.json"
API_KEY_FIELD_NAMES = ("api_key_env", "env_key")


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str
    api_key: str | None
    api_key_source: str | None

    @property
    def endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}/images/generations"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and save images with gpt-image-2 using ~/.codex/config.toml."
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Image generation prompt.")
    prompt_group.add_argument("--prompt-file", type=Path, help="UTF-8 prompt file.")
    parser.add_argument("--output", type=Path, default=Path("generated-image.png"))
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--output-format", choices=("png", "jpeg", "webp"), default="png")
    parser.add_argument("--moderation", choices=("auto", "low"), default="low")
    parser.add_argument("--timeout", type=float, default=1200.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object in {path}")
    return value


def resolve_api_key(provider: dict[str, Any]) -> tuple[str | None, str | None]:
    configured_key = provider.get("api_key")
    if isinstance(configured_key, str) and configured_key.strip():
        return configured_key.strip(), "config:model_provider.api_key"

    for field_name in API_KEY_FIELD_NAMES:
        env_name = provider.get(field_name)
        if isinstance(env_name, str) and env_name.strip():
            value = os.getenv(env_name.strip(), "").strip()
            if value:
                return value, f"environment:{env_name.strip()}"
            raise RuntimeError(
                f"provider field {field_name} requires environment variable {env_name.strip()}"
            )

    if provider.get("requires_openai_auth") is True:
        environment_key = os.getenv("OPENAI_API_KEY", "").strip()
        if environment_key:
            return environment_key, "environment:OPENAI_API_KEY"
        auth = read_json_object(AUTH_PATH)
        auth_key = auth.get("OPENAI_API_KEY")
        if isinstance(auth_key, str) and auth_key.strip():
            return auth_key.strip(), "codex-auth:OPENAI_API_KEY"
        raise RuntimeError(
            f"active provider requires OpenAI auth, but no OPENAI_API_KEY was found in the environment or {AUTH_PATH}"
        )

    return None, None


def resolve_provider(require_api_key: bool) -> ProviderConfig:
    if not CONFIG_PATH.is_file():
        raise RuntimeError(f"Codex config not found: {CONFIG_PATH}")
    config = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    provider_name = config.get("model_provider")
    if not isinstance(provider_name, str) or not provider_name.strip():
        raise RuntimeError(f"model_provider is missing from {CONFIG_PATH}")
    providers = config.get("model_providers")
    if not isinstance(providers, dict):
        raise RuntimeError(f"model_providers is missing from {CONFIG_PATH}")
    provider = providers.get(provider_name)
    if not isinstance(provider, dict):
        raise RuntimeError(f"active provider {provider_name!r} is missing from model_providers")
    base_url = provider.get("base_url")
    if not isinstance(base_url, str) or not base_url.strip():
        raise RuntimeError(f"base_url is missing for active provider {provider_name!r}")
    api_key, api_key_source = resolve_api_key(provider) if require_api_key else (None, None)
    return ProviderConfig(
        name=provider_name.strip(),
        base_url=base_url.strip().rstrip("/"),
        api_key=api_key,
        api_key_source=api_key_source,
    )


def prompt_text(args: argparse.Namespace) -> str:
    value = args.prompt if args.prompt is not None else args.prompt_file.read_text(encoding="utf-8")
    value = value.strip()
    if not value:
        raise ValueError("prompt must not be empty")
    return value


def tls_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    if sys.platform == "darwin":
        result = subprocess.run(
            [
                "security",
                "find-certificate",
                "-a",
                "-p",
                "/System/Library/Keychains/SystemRootCertificates.keychain",
            ],
            capture_output=True,
            check=True,
        )
        context.load_verify_locations(cadata=result.stdout.decode("utf-8"))
    return context


def request_json(
    provider: ProviderConfig,
    payload: dict[str, Any],
    timeout: float,
    context: ssl.SSLContext,
) -> dict[str, Any]:
    if not provider.api_key:
        raise RuntimeError("active provider did not resolve an API key")
    request = urllib.request.Request(
        provider.endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            value = json.loads(response.read().decode("utf-8"))
            if not isinstance(value, dict):
                raise RuntimeError("image provider returned a non-object JSON response")
            return value
    except urllib.error.HTTPError as error:
        body = error.read(4096).decode("utf-8", errors="replace")
        raise RuntimeError(f"image provider returned HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"image provider request failed: {error.reason}") from error


def output_path(base: Path, index: int, count: int, output_format: str) -> Path:
    suffix = f".{output_format}"
    if base.exists() and base.is_dir():
        return base / f"generated-image-{index + 1}{suffix}"
    candidate = base if base.suffix else base.with_suffix(suffix)
    if count == 1:
        return candidate
    return candidate.with_name(f"{candidate.stem}-{index + 1}{candidate.suffix}")


def image_bytes(item: dict[str, Any], timeout: float, context: ssl.SSLContext) -> bytes:
    encoded = item.get("b64_json")
    if isinstance(encoded, str) and encoded:
        return base64.b64decode(encoded, validate=True)
    image_url = item.get("url")
    if isinstance(image_url, str) and image_url:
        with urllib.request.urlopen(image_url, timeout=timeout, context=context) as response:
            return response.read()
    raise RuntimeError("image response item contains neither b64_json nor url")


def main() -> int:
    args = parse_args()
    if not 1 <= args.n <= 16:
        raise ValueError("--n must be between 1 and 16")
    if args.timeout <= 0:
        raise ValueError("--timeout must be positive")

    prompt = prompt_text(args)
    provider = resolve_provider(require_api_key=not args.dry_run)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "n": args.n,
        "size": args.size,
        "quality": args.quality,
        "output_format": args.output_format,
        "moderation": args.moderation,
    }

    if args.dry_run:
        print(
            json.dumps(
                {
                    "config": str(CONFIG_PATH),
                    "provider": provider.name,
                    "url": provider.endpoint,
                    "payload": payload,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    context = tls_context()
    response = request_json(provider, payload, args.timeout, context)
    data = response.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("image provider returned no image data")

    written: list[str] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise RuntimeError("image provider returned an invalid image item")
        path = output_path(args.output.expanduser(), index, len(data), args.output_format).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        content = image_bytes(item, args.timeout, context)
        if not content:
            raise RuntimeError("image provider returned an empty image")
        path.write_bytes(content)
        written.append(str(path))

    summary = {
        "config": str(CONFIG_PATH),
        "provider": provider.name,
        "model": MODEL,
        "outputs": written,
        "usage": response.get("usage"),
        "api_key_source": provider.api_key_source,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)

import json
import os
import re
from pathlib import Path
from typing import Any, TypedDict

from pymonad.either import Either, Left, Right

from functional.alias import Error


class BeaverHabitsConfig(TypedDict):
    url: str
    headers: dict[str, str]


class AppConfig(TypedDict):
    beaverhabits: BeaverHabitsConfig


def _parse_headers(raw: str) -> Either[Error, dict[str, str]]:
    headers: dict[str, str] = {}
    if not raw.strip():
        return Right(headers)

    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            return Left(Error("Invalid header format: Key:Value expected"))
        key, _, value = part.partition(":")
        key = key.strip()
        value = value.strip()
        if not key or not value:
            return Left(Error("Invalid header format: Key:Value expected"))
        headers[key] = value

    return Right(headers)


def _interpolate_env(value: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        return os.environ[var_name]

    return re.sub(r"\{\{\s*(\w+)\s*\}\}", _replace, value)


def _deep_merge(base: dict, override: dict) -> dict:
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> Either[Error, AppConfig]:
    # Config file is the primary mandatory source
    config_file_path = Path.home() / ".config" / "com.kevincojean.beaverhabits-tui" / "config.json"
    if not config_file_path.exists():
        return Left(Error(f"Config file not found at {config_file_path}"))
    try:
        with open(config_file_path) as f:
            file_config: dict[str, Any] = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return Left(Error(f"Failed to read config file: {e}"))

    # Env vars are optional overrides (if set, they take precedence over file config)
    env_config: dict[str, Any] = {}
    url = os.environ.get("BEAVERHABITS_URL")
    if url:
        raw_headers = os.environ.get("BEAVERHABITS_HEADERS", "")
        parsed_headers = _parse_headers(raw_headers)
        if parsed_headers.is_left():
            return parsed_headers  # type: ignore[return-value]
        headers = parsed_headers.value
        env_config = {
            "beaverhabits": {
                "url": url,
                "headers": headers,
            }
        }

    merged = _deep_merge(file_config, env_config)

    beaverhabits = merged.get("beaverhabits", {})
    if not isinstance(beaverhabits, dict):
        return Left(Error("Config 'beaverhabits' must be a dictionary"))

    final_url = beaverhabits.get("url", "")
    if not final_url:
        return Left(Error("BEAVERHABITS_URL is not configured"))

    final_headers = beaverhabits.get("headers", {})
    if not isinstance(final_headers, dict):
        return Left(Error("Config 'headers' must be a dictionary"))

    try:
        final_url = _interpolate_env(final_url)
        final_headers = {k: _interpolate_env(v) for k, v in final_headers.items()}
    except KeyError as e:
        return Left(Error(f"Environment variable {e} is not set"))

    return Right(
        AppConfig(
            beaverhabits=BeaverHabitsConfig(
                url=final_url,
                headers=final_headers,
            )
        )
    )

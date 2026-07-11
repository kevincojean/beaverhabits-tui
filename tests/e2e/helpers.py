import json
import os
import subprocess
from pathlib import Path


def run_cli(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        ["uv", "run", "beaverhabits"] + args,
        capture_output=True,
        text=True,
        env=merged_env,
    )


def create_test_config(dir: str, content: dict) -> str:
    Path(dir).mkdir(parents=True, exist_ok=True)
    config_path = os.path.join(dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(content, f)
    return config_path

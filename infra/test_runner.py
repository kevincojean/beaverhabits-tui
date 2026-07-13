#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer==0.24.2",
#     "rich==15.0.0",
# ]
# ///
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_BIN = PROJECT_ROOT / ".venv" / "bin" / "python"

app = typer.Typer(
    help="Infrastructure CLI for beaverhabits-tui",
    no_args_is_help=True,
)


def _parse_pytest_summary(output: str) -> dict[str, int]:
    match = re.search(
        r"^=+\s+(?=\d)"
        r"(.+?)"
        r"\s+in\s+[\d.]+s"
        r"\s*=+\s*$",
        output,
        re.MULTILINE,
    )
    if not match:
        return {}

    allowed = {"passed", "failed", "xfailed", "xpassed", "warnings", "error", "errors"}
    summary: dict[str, int] = {}
    for entry in re.finditer(r"(\d+)\s+(\w+)", match.group(1)):
        label = entry.group(2)
        if label in allowed:
            summary[label] = int(entry.group(1))
    return summary


def _ensure_config() -> None:
    config_path = os.environ.get("BEAVERHABITS_CONFIG_PATH")
    if not config_path:
        return
    config_file = Path(config_path)
    if config_file.exists():
        return
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        json.dumps(
            {
                "beaverhabits": {"url": "https://example.com", "headers": {}},
                "renderer": {"truncateGraphemes": True},
            }
        )
    )


@app.command()
def test(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose pytest output"),
    ] = False,
    filter: Annotated[
        str | None,
        typer.Option(
            "--filter",
            "-f",
            help="Test filter: 'unit', 'e2e', or path (default: all)",
        ),
    ] = None,
) -> None:
    """Run the test suite with rich output."""
    _ensure_config()
    test_path = "tests"
    if filter == "unit":
        test_path = "tests/unit"
    elif filter == "e2e":
        test_path = "tests/e2e"
    elif filter is not None:
        test_path = filter

    pytest_args = [str(PYTHON_BIN), "-m", "pytest", test_path]
    if verbose:
        pytest_args.append("-v")

    display_args = f".venv/bin/python -m pytest {test_path}"
    if verbose:
        display_args += " -v"

    console.print(
        Panel.fit(
            f"[bold cyan]Running tests:[/bold cyan] {display_args}",
            border_style="cyan",
        )
    )

    start_time = time.time()
    result = subprocess.run(
        pytest_args,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    duration = time.time() - start_time

    combined_output = result.stdout + result.stderr

    spawn_failed = any(
        marker in combined_output
        for marker in ("Failed to spawn", "No module named")
    )
    if result.returncode != 0 and spawn_failed:
        console.print()
        console.print("[bold red]✗ Failed to run pytest[/bold red]")
        console.print(combined_output)
        raise typer.Exit(code=2)

    summary = _parse_pytest_summary(combined_output)

    table = Table(title="Test Results", show_header=True, expand=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right")

    if summary:
        if "passed" in summary:
            table.add_row("Passed", f"[green]{summary['passed']}[/green]")
        if "failed" in summary:
            table.add_row("Failed", f"[red]{summary['failed']}[/red]")
        if "warnings" in summary:
            table.add_row("Warnings", f"[yellow]{summary['warnings']}[/yellow]")
    else:
        table.add_row("Status", "[red]Could not parse test results[/red]")

    table.add_row("Duration", f"{duration:.2f}s")

    console.print()
    console.print(table)

    if result.returncode == 0:
        console.print("\n[bold green]✓ All tests passed[/bold green]")
    else:
        console.print("\n[bold red]✗ Tests failed[/bold red]")
        if not verbose:
            console.print("[dim]Run with --verbose for detailed output[/dim]")
            console.print()
            console.print(combined_output)

    raise typer.Exit(code=result.returncode)


@app.command()
def version() -> None:
    """Show version information."""
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        pkg_version = result.stdout.strip()
    else:
        pkg_version = "dev"

    console.print(f"beaverhabits-tui [cyan]{pkg_version}[/cyan]")


if __name__ == "__main__":
    app()

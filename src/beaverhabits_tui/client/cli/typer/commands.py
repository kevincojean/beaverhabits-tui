from __future__ import annotations

from typing import final

import typer
from rich.console import Console

from beaverhabits_tui.client.http.httpx.http_client import HttpClient
from beaverhabits_tui.client.http.httpx.habits_client import HabitsClient
from beaverhabits_tui.configuration.configuration import load_config
from beaverhabits_tui.views.rich.render import default_view

console = Console()


@final
class Commands:
    """Collection of CLI commands for the beaverhabits TUI."""

    def default_cmd(self) -> None:
        # Lazy import to avoid circular dependency with app.py (T12)
        from beaverhabits_tui.app import configure_injector  # noqa: PLC0415

        import inject  # noqa: PLC0415

        inject.clear_and_configure(configure_injector)

        config_result = load_config()
        if config_result.is_left():
            msg = config_result.either(lambda e: e.message, lambda _: "")
            console.print(f"[red]Error: {msg}[/red]")
            raise typer.Exit(code=1)

        config = config_result.either(lambda _: None, lambda r: r)
        bh_config = config["beaverhabits"]

        http_client = HttpClient(bh_config["url"], bh_config["headers"])
        habits_client = HabitsClient(http_client)

        list_result = habits_client.list_habits()
        if list_result.is_left():
            msg = list_result.either(lambda e: e.message, lambda _: "")
            console.print(f"[red]Error: {msg}[/red]")
            raise typer.Exit(code=1)

        habits_list = list_result.either(lambda _: [], lambda r: r)

        from beaverhabits_tui.models.habit import HabitDetail  # noqa: PLC0415

        details: list[HabitDetail] = []
        for hl in habits_list:
            detail_result = habits_client.get_habit(hl.id)
            if detail_result.is_right():
                details.append(detail_result.either(lambda _: None, lambda r: r))

        output = default_view(details)
        console.print(output)


app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    Commands().default_cmd()

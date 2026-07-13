import inject

from beaverhabits_tui.client.http.httpx.habits_client import HabitsClient
from beaverhabits_tui.client.http.httpx.http_client import HttpClient
from beaverhabits_tui.client.http.httpx.user_client import UserClient
from beaverhabits_tui.configuration.configuration import load_config
from beaverhabits_tui.services.grapheme_truncator import (
    GraphemeTruncator,
    NoOpTruncator,
    RichGraphemeTruncator,
)


def configure_injector(binder: inject.Binder) -> None:
    config_result = load_config()
    if config_result.is_left():
        raise RuntimeError(config_result.either(lambda e: e.message, lambda _: "Config error"))
    config = config_result.either(lambda _: None, lambda r: r)
    bh_config = config["beaverhabits"]
    renderer_config = config["renderer"]

    http_client = HttpClient(bh_config["url"], bh_config["headers"])
    binder.bind(HttpClient, http_client)
    binder.bind(HabitsClient, HabitsClient(http_client))
    binder.bind(UserClient, UserClient(http_client))

    if renderer_config["truncateGraphemes"]:
        binder.bind(GraphemeTruncator, RichGraphemeTruncator())
    else:
        binder.bind(GraphemeTruncator, NoOpTruncator())


from beaverhabits_tui.client.cli.typer.commands import app  # noqa: E402, F401

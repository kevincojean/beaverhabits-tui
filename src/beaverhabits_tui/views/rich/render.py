from __future__ import annotations

import datetime
from collections import defaultdict

from rich.table import Table
from rich.text import Text
from rich import box

from beaverhabits_tui.models.habit import HabitDetail
from beaverhabits_tui.services.grapheme_truncator import GraphemeTruncator

__all__ = ["default_view"]

NAME_WIDTH = 35


def default_view(habits: list[HabitDetail], truncator: GraphemeTruncator) -> Table:
    """Render a tagged 5-day habit grid as a Rich Table.

    Returns a Table object suitable for ``rich.console.Console.print``.
    """
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(4, -1, -1)]

    table = Table(
        show_header=True,
        show_edge=False,
        show_lines=False,
        padding=(0, 2),
        expand=False,
        header_style="",
        box=box.SIMPLE,
    )

    table.add_column("Habit", style="", width=NAME_WIDTH, no_wrap=True)
    for d in dates:
        label = d.strftime("%a %d")
        table.add_column(label, justify="center", width=8, no_wrap=True)

    tagged: dict[str, list[HabitDetail]] = defaultdict(list)
    untagged: list[HabitDetail] = []
    for h in habits:
        if h.tags:
            primary = sorted(h.tags)[0]
            tagged[primary].append(h)
        else:
            untagged.append(h)

    def sort_key(h: HabitDetail) -> tuple[int, str]:
        return (0 if h.star else 1, h.name.lower())

    for group in tagged.values():
        group.sort(key=sort_key)
    untagged.sort(key=sort_key)

    date_strings = [d.isoformat() for d in dates]
    record_maps: dict[str, dict[str, bool]] = {}

    tag_keys = sorted(tagged)
    for i, tag in enumerate(tag_keys):
        if i > 0:
            table.add_row(Text(""), Text(""), Text(""), Text(""), Text(""), Text(""))
        table.add_row(
            Text(f"#{tag}", style="blue"),
            Text(""),
            Text(""),
            Text(""),
            Text(""),
            Text(""),
        )
        for habit in tagged[tag]:
            record_maps[habit.id] = {r.data.day: r.data.done for r in habit.records}
            table.add_row(*_habit_row(habit, date_strings, record_maps[habit.id], truncator))

    if untagged:
        if tagged:
            table.add_row(Text(""), Text(""), Text(""), Text(""), Text(""), Text(""))
        for habit in untagged:
            record_maps[habit.id] = {r.data.day: r.data.done for r in habit.records}
            table.add_row(*_habit_row(habit, date_strings, record_maps[habit.id], truncator))

    return table


def _habit_row(
    habit: HabitDetail,
    date_strings: list[str],
    record_map: dict[str, bool],
    truncator: GraphemeTruncator,
) -> list[Text]:
    name = truncator.truncate(habit.name, NAME_WIDTH)
    row: list[Text] = [Text(truncator.pad(name, NAME_WIDTH))]
    for ds in date_strings:
        done = record_map.get(ds, False)
        if done:
            row.append(Text("✓", style="bold green"))
        else:
            row.append(Text("✘", style="red"))
    return row

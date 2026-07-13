from __future__ import annotations

import datetime
from collections import defaultdict

from beaverhabits_tui.models.habit import HabitDetail

__all__ = ["default_view"]

COLUMN_WIDTH = 8
NAME_WIDTH = 35


def default_view(habits: list[HabitDetail]) -> str:
    """Render a tagged 5-day habit grid using Rich markup.

    Returns a string with Rich markup tags suitable for
    ``rich.console.Console.print``.
    """
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(4, -1, -1)]

    lines: list[str] = []

    header = " " * NAME_WIDTH
    for d in dates:
        label = d.strftime("%a %d")
        header += f"{label:^{COLUMN_WIDTH}}"
    lines.append(header.rstrip())
    lines.append("")

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

    tag_keys = sorted(tagged)
    for i, tag in enumerate(tag_keys):
        if i > 0:
            lines.append("")
        lines.append(f"[blue]#{tag}[/blue]")
        for habit in tagged[tag]:
            lines.append(_habit_line(habit, date_strings))

    if untagged:
        if tagged:
            lines.append("")
        for habit in untagged:
            lines.append(_habit_line(habit, date_strings))

    return "\n".join(lines)


def _habit_line(habit: HabitDetail, date_strings: list[str]) -> str:
    record_map = {r.data.day: r.data.done for r in habit.records}
    if len(habit.name) > NAME_WIDTH:
        name = habit.name[: NAME_WIDTH - 1] + "…"
    else:
        name = habit.name
    line = f"{name:<{NAME_WIDTH}}"
    for ds in date_strings:
        done = record_map.get(ds, False)
        char = "✓" if done else "✘"
        block = char.center(COLUMN_WIDTH)
        if done:
            block = block.replace(char, f"[bold green]{char}[/bold green]")
        else:
            block = block.replace(char, f"[red]{char}[/red]")
        line += block
    return line

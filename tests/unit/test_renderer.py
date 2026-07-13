from __future__ import annotations

import datetime
import io
import re
from unittest.mock import patch

import pytest
from rich.console import Console

from beaverhabits_tui.models.habit import HabitDetail, HabitRecord, HabitRecordData
from beaverhabits_tui.views.rich.render import COLUMN_WIDTH, NAME_PADDING, NAME_WIDTH, default_view


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_rich(text: str) -> str:
    """Remove Rich markup tags, preserving visible characters and spacing."""
    return re.sub(r"\[/?\w+(?:[ =][^\]]+)?\]", "", text)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from Rich console output."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


def data_lines(plain: str) -> list[str]:
    """Extract habit data lines (skipping header, empty, and tag-marker lines).

    A data line has non-whitespace content in the name column (first NAME_WIDTH
    characters). The header has only whitespace there; tag lines start with ``#``.
    """
    return [
        l
        for l in plain.split("\n")
        if len(l) > NAME_WIDTH + 5  # at least 1 name char + almost-full grid
        and not l[:NAME_WIDTH].isspace()  # has a name
        and not l.strip().startswith("#")  # not a tag line
    ]


def make_habit(
    name: str,
    *,
    done_days: list[int] | None = None,
    tags: list[str] | None = None,
    star: bool = False,
) -> HabitDetail:
    """Create a HabitDetail with records for the last 5 days.

    *done_days* controls which of the 5 most recent days are marked done
    (0 = most recent, 4 = least recent).  Default: none done.
    """
    done_days = done_days or []
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(4, -1, -1)]
    records = [
        HabitRecord(data=HabitRecordData(day=d.isoformat(), done=(4 - i in done_days)))
        for i, d in enumerate(dates)
    ]
    return HabitDetail(
        id=name.lower().replace(" ", "-"),
        name=name,
        star=star,
        records=records,
        status="active",
        tags=tags or [],
    )


# ---------------------------------------------------------------------------
# Alignment tests
# ---------------------------------------------------------------------------

def _assert_cells(habit_line: str) -> None:
    """Assert every cell in the habit line is exactly COLUMN_WIDTH wide (display-aware)."""
    from rich.cells import cell_len, set_cell_size
    
    for col in range(5):
        start_display = NAME_WIDTH + NAME_PADDING + col * COLUMN_WIDTH
        
        # Find string position that corresponds to display position
        str_pos = 0
        display_pos = 0
        while display_pos < start_display and str_pos < len(habit_line):
            char = habit_line[str_pos]
            display_pos += cell_len(char)
            str_pos += 1
        
        # Extract cell by display width
        remaining = habit_line[str_pos:]
        cell = set_cell_size(remaining, COLUMN_WIDTH)
        
        assert cell_len(cell) == COLUMN_WIDTH, (
            f"Cell {col} display width {cell_len(cell)} != {COLUMN_WIDTH}: {repr(cell)}"
        )


def _assert_cell_content(habit_line: str, expected: str) -> None:
    """Assert every cell contains the expected character (✓ or ✘) (display-aware)."""
    from rich.cells import cell_len, set_cell_size
    
    for col in range(5):
        start_display = NAME_WIDTH + NAME_PADDING + col * COLUMN_WIDTH
        
        str_pos = 0
        display_pos = 0
        while display_pos < start_display and str_pos < len(habit_line):
            char = habit_line[str_pos]
            display_pos += cell_len(char)
            str_pos += 1
        
        remaining = habit_line[str_pos:]
        cell = set_cell_size(remaining, COLUMN_WIDTH)
        
        assert expected in cell, f"Cell {col} missing {expected}: {repr(cell)}"


# ---------------------------------------------------------------------------
# Alignment tests
# ---------------------------------------------------------------------------

class TestGridAlignment:

    def test_all_not_done_shows_crosses(self):
        habits = [make_habit("Test Habit")]
        rows = data_lines(strip_rich(default_view(habits)))
        _assert_cells(rows[0])
        _assert_cell_content(rows[0], "✘")

    def test_all_done_shows_checkmarks(self):
        habits = [make_habit("Test Habit", done_days=[0, 1, 2, 3, 4])]
        rows = data_lines(strip_rich(default_view(habits)))
        _assert_cells(rows[0])
        _assert_cell_content(rows[0], "✓")

    def test_mixed_columns_each_exactly_eight(self):
        habits = [make_habit("Test Habit", done_days=[1, 3])]
        rows = data_lines(strip_rich(default_view(habits)))
        _assert_cells(rows[0])

    def test_header_columns_align_with_data_columns(self):
        habits = [make_habit("Align Check", done_days=[0, 4])]
        plain = strip_rich(default_view(habits))
        lines = plain.split("\n")

        header = next(l for l in lines if l.strip())
        rows = data_lines(plain)

        for col in range(5):
            h_start = NAME_WIDTH + NAME_PADDING + col * COLUMN_WIDTH
            d_start = NAME_WIDTH + NAME_PADDING + col * COLUMN_WIDTH

            h_cell = header[h_start : h_start + COLUMN_WIDTH]
            d_cell = rows[0][d_start : d_start + COLUMN_WIDTH]

            assert any(
                day in h_cell
                for day in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
            ), f"Header cell {col} missing day name: {repr(h_cell)}"

            assert "✓" in d_cell or "✘" in d_cell, (
                f"Data cell {col} missing ✓/✘: {repr(d_cell)}"
            )

    def test_header_same_length_as_data_lines(self):
        habits = [make_habit("Length Check")]
        lines = default_view(habits).split("\n")

        header = strip_rich(lines[0])
        rows = data_lines(strip_rich(default_view(habits)))

        assert len(header) == len(rows[0]), (
            f"Header ({len(header)}) != data ({len(rows[0])})"
        )

    def test_multiple_habits_align(self):
        habits = [
            make_habit("First Habit", done_days=[0]),
            make_habit("Second Habit", done_days=[2]),
            make_habit("Third Habit", done_days=[4]),
        ]
        rows = data_lines(strip_rich(default_view(habits)))
        for row in rows:
            _assert_cells(row)

    def test_long_name_truncation_preserves_alignment(self):
        long_name = "A" * (NAME_WIDTH + 20)
        habits = [make_habit(long_name)]
        rows = data_lines(strip_rich(default_view(habits)))

        name_part = rows[0][:NAME_WIDTH]
        assert len(name_part) == NAME_WIDTH, (
            f"Name part width {len(name_part)} != {NAME_WIDTH}: {repr(name_part)}"
        )
        assert "…" in name_part, (
            f"Truncated name missing ellipsis: {repr(name_part)}"
        )

    def test_rich_markup_does_not_affect_alignment(self):
        habits = [make_habit("Markup Test", done_days=[0, 1])]
        output = default_view(habits)
        rows = data_lines(strip_rich(output))

        for col in range(5):
            start = NAME_WIDTH + NAME_PADDING + col * COLUMN_WIDTH
            raw_cell = rows[0][start : start + COLUMN_WIDTH]
            assert len(raw_cell) == COLUMN_WIDTH, (
                f"Cell {col}: stripped length {len(raw_cell)} != {COLUMN_WIDTH}: "
                f"{repr(raw_cell)}"
            )

    def test_tagged_and_untagged_habits_align(self):
        habits = [
            make_habit("Tagged One", tags=["health"], done_days=[0]),
            make_habit("Untagged One", done_days=[2]),
        ]
        rows = data_lines(strip_rich(default_view(habits)))
        for row in rows:
            _assert_cells(row)

    def test_emoji_names_align_with_ascii_names(self):
        """Emoji in names (2-column wide) must not shift the grid."""
        from rich.cells import cell_len

        habits = [
            make_habit("🌆 Followed my evening routine", done_days=[0], tags=["evening"]),
            make_habit("💊 Take medication", done_days=[1], tags=["morning"]),
            make_habit("🇪🇪 Schedule - Place to discover", done_days=[2], tags=["morning"]),
            make_habit("Plain ASCII name", done_days=[3], tags=["health"]),
        ]
        output = default_view(habits)
        buf = io.StringIO()
        console = Console(file=buf, width=200, color_system=None)
        console.print(output)
        rendered = strip_ansi(buf.getvalue())

        rows = data_lines(rendered)
        for row in rows:
            assert cell_len(row) == NAME_WIDTH + NAME_PADDING + 5 * COLUMN_WIDTH, (
                f"Display width {cell_len(row)} != {NAME_WIDTH + NAME_PADDING + 5 * COLUMN_WIDTH}: "
                f"{repr(row[:40])}"
            )
            _assert_cells(row)

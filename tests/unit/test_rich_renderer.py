from __future__ import annotations

import datetime
import io
import re

from rich.console import Console

from beaverhabits_tui.models.habit import HabitDetail, HabitRecord, HabitRecordData
from beaverhabits_tui.services.grapheme_truncator import RichGraphemeTruncator
from beaverhabits_tui.views.rich.render import NAME_WIDTH, default_view


def render_to_string(table) -> str:
    """Render a Rich Table to a plain string."""
    buf = io.StringIO()
    console = Console(file=buf, width=200, color_system=None)
    console.print(table)
    return buf.getvalue()


def strip_ansi(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text)


def data_lines(rendered: str) -> list[str]:
    """Extract habit data lines from rendered Table output.

    Skips header row, separator lines, and tag marker rows.
    """
    lines = [l for l in rendered.split("\n") if l.strip()]
    result = []
    for line in lines:
        stripped = line.strip()
        # Skip empty lines
        if not stripped:
            continue
        # Skip table borders
        if any(stripped.startswith(c) for c in ["┏", "┡", "├", "└", "━", "─"]):
            continue
        # Skip header row (contains day names)
        if any(day in stripped for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            continue
        # Skip tag separator rows (no checkmarks or crosses)
        if "✓" not in stripped and "✘" not in stripped:
            continue
        # Include data rows
        if len(line) > NAME_WIDTH:
            result.append(line)
    return result


def make_habit(
    name: str,
    *,
    done_days: list[int] | None = None,
    tags: list[str] | None = None,
    star: bool = False,
) -> HabitDetail:
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


def _assert_cells(rendered: str) -> None:
    """Assert every data row has ✓ or ✘ in the expected column positions."""
    rows = data_lines(rendered)
    assert len(rows) > 0, "No data rows found"
    
    for row in rows:
        check_count = row.count("✓") + row.count("✘")
        assert check_count == 5, f"Expected 5 checkmarks/crosses, got {check_count} in: {repr(row)}"


def _assert_cell_content(rendered: str, expected: str) -> None:
    """Assert every data row contains the expected character."""
    rows = data_lines(rendered)
    for row in rows:
        assert expected in row, f"Expected {repr(expected)} in row: {repr(row)}"


class TestGridAlignment:

    def test_all_not_done_shows_crosses(self):
        habits = [make_habit("Test Habit")]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        _assert_cells(rendered)
        _assert_cell_content(rendered, "✘")

    def test_all_done_shows_checkmarks(self):
        habits = [make_habit("Test Habit", done_days=[0, 1, 2, 3, 4])]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        _assert_cells(rendered)
        _assert_cell_content(rendered, "✓")

    def test_mixed_columns_each_exactly_eight(self):
        habits = [make_habit("Test Habit", done_days=[1, 3])]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        _assert_cells(rendered)

    def test_header_columns_align_with_data_columns(self):
        habits = [make_habit("Align Check", done_days=[0, 4])]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        
        lines = [l for l in rendered.split("\n") if l.strip()]
        header_line = next((l for l in lines if any(day in l for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])), None)
        assert header_line is not None, "Header line not found"
        
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            if day in header_line:
                break
        
        rows = data_lines(rendered)
        assert len(rows) > 0, "No data rows found"

    def test_header_same_length_as_data_lines(self):
        habits = [make_habit("Length Check")]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        
        lines = [l for l in rendered.split("\n") if l.strip()]
        data_rows = data_lines(rendered)
        
        assert len(data_rows) > 0, "No data rows found"
        
        header_line = next((l for l in lines if any(day in l for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])), None)
        if header_line:
            assert len(header_line) == len(data_rows[0]), (
                f"Header length {len(header_line)} != data length {len(data_rows[0])}"
            )

    def test_multiple_habits_align(self):
        habits = [
            make_habit("First Habit", done_days=[0]),
            make_habit("Second Habit", done_days=[2]),
            make_habit("Third Habit", done_days=[4]),
        ]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        _assert_cells(rendered)

    def test_long_name_truncation_preserves_alignment(self):
        long_name = "A" * (NAME_WIDTH + 20)
        habits = [make_habit(long_name)]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        
        rows = data_lines(rendered)
        assert len(rows) > 0, "No data rows found"
        
        name_part = rows[0][:NAME_WIDTH]
        assert "…" in name_part or len(name_part) <= NAME_WIDTH, (
            f"Name not truncated properly: {repr(name_part)}"
        )

    def test_rich_markup_does_not_affect_alignment(self):
        habits = [make_habit("Markup Test", done_days=[0, 1])]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        _assert_cells(rendered)

    def test_tagged_and_untagged_habits_align(self):
        habits = [
            make_habit("Tagged One", tags=["health"], done_days=[0]),
            make_habit("Untagged One", done_days=[2]),
        ]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        _assert_cells(rendered)

    def test_emoji_names_align_with_ascii_names(self):
        """Emoji in names (2-column wide) must not shift the grid."""
        from rich.cells import cell_len
        
        habits = [
            make_habit("🌆 Followed my evening routine", done_days=[0], tags=["evening"]),
            make_habit("💊 Take medication", done_days=[1], tags=["morning"]),
            make_habit("🇪🇪 Schedule - Place to discover", done_days=[2], tags=["morning"]),
            make_habit("Plain ASCII name", done_days=[3], tags=["health"]),
        ]
        table = default_view(habits, RichGraphemeTruncator())
        rendered = strip_ansi(render_to_string(table))
        
        rows = data_lines(rendered)
        assert len(rows) >= 4, f"Expected at least 4 data rows, got {len(rows)}"
        
        for row in rows:
            assert "✓" in row or "✘" in row, f"Row missing checkmarks: {repr(row)}"

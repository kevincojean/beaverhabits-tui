from __future__ import annotations

from typing import Protocol

from rich.cells import cell_len, set_cell_size


class GraphemeTruncator(Protocol):
    def truncate(self, text: str, max_width: int) -> str:
        """Truncate text to fit within max_width display columns."""
        ...

    def pad(self, text: str, width: int) -> str:
        """Pad text to exactly width display columns."""
        ...


class RichGraphemeTruncator:
    """Truncates and pads text based on display width using Rich's cell utilities."""

    def truncate(self, text: str, max_width: int) -> str:
        if cell_len(text) <= max_width:
            return text
        return set_cell_size(text, max_width - 1) + "…"

    def pad(self, text: str, width: int) -> str:
        return set_cell_size(text, width)


class NoOpTruncator:
    """No-op truncator that returns text as-is."""

    def truncate(self, text: str, max_width: int) -> str:
        return text

    def pad(self, text: str, width: int) -> str:
        return text.ljust(width)

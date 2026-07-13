# BeaverHabits TUI

Terminal UI for [BeaverHabits](https://beaverhabits.com/) habit tracker. Displays a tagged 5-day habit grid from a configured API endpoint.

> **Status**: Read-only utility. Views habit data from your server — no create, edit, or delete operations.
>
> **Stability**: Versions tagged with `rc` (release candidate) are not production-ready. They work and are usable, but should be considered "ok, not proven stable".

## Install

```bash
uv tool install beaverhabits-tui
```

Or from source:

```bash
git clone https://github.com/kevincojean/beaverhabits-tui.git
cd beaverhabits-tui
uv sync
```

Requires Python >= 3.10.

## Configure

Configuration is loaded from a JSON file at `~/.config/com.kevincojean.beaverhabits-tui/config.json`. This file is **mandatory**.  
You may add *optional* extra headers, depending on your needs and where you deployed a beaverhabits instance.  

```json
{
  "beaverhabits": {
    "url": "https://habits.example.com",
    "headers": {
      "Authorization": "Basic {base64-encoded - username:password}"
    }
  },
  "renderer": {
    "truncateGraphemes": true
  }
}
```

The `renderer.truncateGraphemes` option controls how habit names are truncated:
- `true` (default): Truncates based on display width, ensuring grid alignment with emoji and wide characters
- `false`: Truncates based on character count, which may cause misalignment with emoji

Environment variables are **optional overrides** — if set, they take precedence over the config file:

```bash
export BEAVERHABITS_CONFIG_PATH="/path/to/config.json"
export BEAVERHABITS_URL="https://habits.example.com"
export BEAVERHABITS_HEADERS="Authorization:Bearer <token>;X-Debug:1"
```

`BEAVERHABITS_CONFIG_PATH` overrides the default config file location (`~/.config/com.kevincojean.beaverhabits-tui/config.json`).
`BEAVERHABITS_URL` and `BEAVERHABITS_HEADERS` override the corresponding values in the config file.

Headers are semicolon-separated `Key:Value` pairs.

Supports `{{ VAR }}` interpolation for values referencing other env vars.

## Usage

```bash
beaverhabits
```

Outputs a 5-day habit grid grouped by tag:

```
                         Wed 08   Thu 09   Fri 10   Sat 11   Sun 12

#fitness
  Running                ✓         ·         ·         ✓         ·
  Stretching             ·         ·         ✓         ·         ·

#health
  Meditation             ✓         ✓         ✓         ✓         ·

  Call mom               ·         ✓         ·         ·         ·
```

- `✓` = done (green), `·` = not done (dim)
- Habits grouped by tag, starred habits first
- Untagged habits listed at the bottom

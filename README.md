# BeaverHabits TUI

Terminal UI for [BeaverHabits](https://beaverhabits.com/) habit tracker. Displays a tagged 5-day habit grid from a configured API endpoint.

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

Set your server URL and authentication headers:

```bash
export BEAVERHABITS_URL="https://habits.example.com"
export BEAVERHABITS_HEADERS="Authorization:Bearer <token>;X-Debug:1"
```

Headers are semicolon-separated `Key:Value` pairs.

Config file at `~/.config/com.kevincojean.beaverhabits-tui/config.json`:

```json
{
  "beaverhabits": {
    "url": "https://habits.example.com",
    "headers": {
      "Authorization": "Bearer <token>"
    }
  }
}
```

Env vars take precedence over the config file.

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

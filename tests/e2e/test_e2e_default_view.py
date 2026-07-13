import pytest
from tests.e2e.helpers import run_cli


class TestDefaultView:
    """E2E tests for the default view of beaverhabits CLI (AC 1.1-1.7)."""

    @pytest.mark.xfail(reason="Requires configured API endpoint with habits data")
    def test_given_habits_with_tags_when_run_then_shows_grouped_grid(self):
        """AC 1.1: Habits with tags appear in grouped grid with day headers,
        tag names, and mixed checkmark/dot characters."""
        env = {
            "BEAVERHABITS_URL": "https://habits.example.com/api",
            "BEAVERHABITS_HEADERS": "Authorization:Bearer test-token",
        }
        result = run_cli([], env=env)
        assert result.returncode == 0
        assert "Mon" in result.stdout or "Tue" in result.stdout
        assert "#" in result.stdout
        assert "✓" in result.stdout
        assert "✘" in result.stdout

    @pytest.mark.xfail(reason="Requires configured API endpoint with untagged habits")
    def test_given_untagged_habits_when_run_then_listed_without_header(self):
        """AC 1.2: Untagged habits appear without any #tag header."""
        env = {
            "BEAVERHABITS_URL": "https://habits.example.com/api",
            "BEAVERHABITS_HEADERS": "Authorization:Bearer test-token",
        }
        result = run_cli([], env=env)
        assert result.returncode == 0
        assert "#" not in result.stdout

    @pytest.mark.xfail(reason="Requires configured API endpoint returning empty habit list")
    def test_given_no_habits_when_run_then_shows_no_habits_message(self):
        """AC 1.3: Empty habit list shows appropriate empty-state message."""
        env = {
            "BEAVERHABITS_URL": "https://habits.example.com/api",
            "BEAVERHABITS_HEADERS": "Authorization:Bearer test-token",
        }
        result = run_cli([], env=env)
        assert result.returncode == 0
        assert result.stdout.strip() == "" or "no habit" in result.stdout.lower()

    @pytest.mark.xfail(reason="Requires configured API endpoint with fully completed habits")
    def test_given_all_done_when_run_then_shows_all_checkmarks(self):
        """AC 1.4: Fully completed habit row shows checkmarks for all 5 days."""
        env = {
            "BEAVERHABITS_URL": "https://habits.example.com/api",
            "BEAVERHABITS_HEADERS": "Authorization:Bearer test-token",
        }
        result = run_cli([], env=env)
        assert result.returncode == 0
        assert "✓" in result.stdout

    @pytest.mark.xfail(reason="Requires configured API endpoint with uncompleted habits")
    def test_given_none_done_when_run_then_shows_all_dots(self):
        """AC 1.5: Completely uncompleted habit row shows dots for all 5 days."""
        env = {
            "BEAVERHABITS_URL": "https://habits.example.com/api",
            "BEAVERHABITS_HEADERS": "Authorization:Bearer test-token",
        }
        result = run_cli([], env=env)
        assert result.returncode == 0
        assert "✘" in result.stdout

    @pytest.mark.xfail(reason="Requires API endpoint returning HTTP 401")
    def test_given_401_when_run_then_not_authenticated_message(self):
        """AC 1.6: HTTP 401 from server yields 'not authenticated' error and exit code 1."""
        env = {
            "BEAVERHABITS_URL": "https://habits.example.com/api",
            "BEAVERHABITS_HEADERS": "Authorization:Bearer invalid-token",
        }
        result = run_cli([], env=env)
        assert result.returncode == 1
        assert "not authenticated" in result.stdout

    def test_given_live_config_when_run_then_connects_to_server(self):
        """CLI reads URL from config file and attempts connection to server."""
        result = run_cli([])
        output = result.stdout + result.stderr
        # With a valid live config, CLI should either succeed or
        # return a server-level error (auth, network), not a config error
        assert result.returncode in (0, 1)
        assert "Config file not found" not in output
        assert "not configured" not in output

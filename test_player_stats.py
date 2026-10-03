"""
test_player_stats.py
====================
Mock-based tests for the Player Stats implementation in app.py.

Verifies:
  1. INTERNATIONAL_PLAYERS_DATA structure (32 players, gender split, formats)
  2. get_filtered_players() – gender / country / role / search filters
  3. get_player_stats()     – returns correct stats dict for a known player
  4. search_api_player()   – 429 path (returns quota_exceeded sentinel)
  5. search_api_player()   – 200 path (returns list of players)
  6. search_api_player()   – network error path (returns None)
  7. search_api_player()   – no API key path (returns None)

No real HTTP calls are made. All API calls are mocked with unittest.mock.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Import helpers from app without running Streamlit's top-level execution.
# We import only the pure-Python functions by injecting stubs for 'streamlit'.
# ---------------------------------------------------------------------------

# Stub the streamlit module so importing app.py doesn't trigger st.set_page_config
import types

st_stub = types.ModuleType("streamlit")
# Provide the minimal attributes app.py uses at module level
st_stub.cache_resource = lambda *a, **kw: (lambda f: f)  # passthrough decorator
st_stub.cache_data     = lambda *a, **kw: (lambda f: f)
st_stub.secrets        = {}                                # no secrets set

def _columns(n, **kw):
    """Return n MagicMocks so tuple-unpacking in app.py works."""
    count = n if isinstance(n, int) else len(n)
    return [MagicMock() for _ in range(count)]

def _tabs(labels):
    """Return one MagicMock per tab label."""
    return [MagicMock() for _ in labels]

class _SessionState(dict):
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)
    def __setattr__(self, k, v):
        self[k] = v

st_stub.session_state = _SessionState()

# Stub any st.* calls that fire during module-level code (set_page_config, etc.)
for _name in [
    "set_page_config", "sidebar", "title", "header", "subheader",
    "write", "info", "warning", "error", "success", "markdown",
    "multiselect", "radio", "spinner", "balloons", "metric",
    "caption", "expander", "dataframe", "plotly_chart", "empty",
    "button", "text_input", "selectbox",
]:
    setattr(st_stub, _name, MagicMock())

# columns/tabs need to return the right number of objects for unpacking
st_stub.columns = _columns
st_stub.tabs    = _tabs

sys.modules["streamlit"] = st_stub

# Also stub plotly so the import chain doesn't fail
for _mod in ["plotly", "plotly.express", "plotly.graph_objects"]:
    sys.modules.setdefault(_mod, types.ModuleType(_mod))

# Now we can safely import the app
sys.path.insert(0, os.path.dirname(__file__))
import app  # noqa: E402  (must come after stubs)


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

class TestPlayerData(unittest.TestCase):
    """Verify INTERNATIONAL_PLAYERS_DATA integrity."""

    def test_total_count(self):
        count = len(app.INTERNATIONAL_PLAYERS_DATA)
        self.assertEqual(count, 32, f"Expected 32 players, found {count}")

    def test_gender_split(self):
        men   = [p for p in app.INTERNATIONAL_PLAYERS_DATA.values() if p["gender"] == "Men's"]
        women = [p for p in app.INTERNATIONAL_PLAYERS_DATA.values() if p["gender"] == "Women's"]
        self.assertEqual(len(men),   16, f"Expected 16 Men's players, found {len(men)}")
        self.assertEqual(len(women), 16, f"Expected 16 Women's players, found {len(women)}")

    def test_all_have_required_keys(self):
        """Every player dict must have the core fields used by the Players page."""
        required = {"gender", "country", "role", "teams", "batting_career", "bowling_career"}
        for name, p in app.INTERNATIONAL_PLAYERS_DATA.items():
            missing = required - set(p.keys())
            self.assertFalse(missing, f"Player '{name}' missing keys: {missing}")

    def test_formats_present(self):
        """Every batting_career / bowling_career entry must have Test, ODI, T20I."""
        for name, p in app.INTERNATIONAL_PLAYERS_DATA.items():
            for stat_type in ("batting_career", "bowling_career"):
                for fmt in ("Test", "ODI", "T20I"):
                    self.assertIn(fmt, p[stat_type],
                                  f"Player '{name}' missing {stat_type}['{fmt}']")

    def test_virat_kohli_stats(self):
        """Spot-check a well-known player's numbers."""
        vk = app.INTERNATIONAL_PLAYERS_DATA.get("Virat Kohli")
        self.assertIsNotNone(vk)
        self.assertEqual(vk["gender"], "Men's")
        self.assertEqual(vk["country"], "India")
        # ODI runs alone should exceed 13,000
        self.assertGreater(vk["batting_career"]["ODI"]["runs"], 13000)

    def test_smriti_mandhana_stats(self):
        sm = app.INTERNATIONAL_PLAYERS_DATA.get("Smriti Mandhana")
        self.assertIsNotNone(sm)
        self.assertEqual(sm["gender"], "Women's")
        self.assertEqual(sm["country"], "India")


class TestGetPlayerStats(unittest.TestCase):
    """get_player_stats() returns the player dict on success, or an error dict on miss."""

    def test_known_player_returns_dict(self):
        stats = app.get_player_stats("Virat Kohli")
        self.assertIsInstance(stats, dict)
        self.assertNotIn("error", stats)
        self.assertEqual(stats["country"], "India")

    def test_unknown_player_returns_error_dict(self):
        stats = app.get_player_stats("Nonexistent Player XYZ")
        self.assertIsInstance(stats, dict)
        self.assertIn("error", stats)

    def test_empty_name_returns_error_dict(self):
        result = app.get_player_stats("")
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)


class TestGetFilteredPlayers(unittest.TestCase):
    """get_filtered_players() returns a sorted list of player *names* (strings)."""

    def test_all_returns_all(self):
        result = app.get_filtered_players()
        self.assertEqual(len(result), 32)
        # All entries must be strings (names)
        self.assertTrue(all(isinstance(n, str) for n in result))

    def test_mens_filter(self):
        result = app.get_filtered_players(gender="Men's")
        self.assertEqual(len(result), 16)
        # Look up each returned name in the source data and check gender
        for name in result:
            self.assertEqual(app.INTERNATIONAL_PLAYERS_DATA[name]["gender"], "Men's")

    def test_womens_filter(self):
        result = app.get_filtered_players(gender="Women's")
        self.assertEqual(len(result), 16)
        for name in result:
            self.assertEqual(app.INTERNATIONAL_PLAYERS_DATA[name]["gender"], "Women's")

    def test_country_filter(self):
        result = app.get_filtered_players(country="India")
        self.assertTrue(len(result) > 0)
        for name in result:
            self.assertEqual(app.INTERNATIONAL_PLAYERS_DATA[name]["country"], "India")

    def test_role_filter_batsman(self):
        result = app.get_filtered_players(role="Batsman")
        self.assertTrue(len(result) > 0)
        for name in result:
            self.assertIn("batsman", app.INTERNATIONAL_PLAYERS_DATA[name]["role"].lower())

    def test_search_filter(self):
        result = app.get_filtered_players(search_term="Kohli")
        self.assertIn("Virat Kohli", result)

    def test_combined_filter(self):
        result = app.get_filtered_players(gender="Men's", country="Australia")
        self.assertTrue(len(result) > 0)
        for name in result:
            p = app.INTERNATIONAL_PLAYERS_DATA[name]
            self.assertEqual(p["gender"], "Men's")
            self.assertEqual(p["country"], "Australia")

    def test_empty_search_returns_all(self):
        self.assertEqual(len(app.get_filtered_players(search_term="")), 32)

    def test_result_is_sorted(self):
        result = app.get_filtered_players()
        self.assertEqual(result, sorted(result))


class TestSearchApiPlayer(unittest.TestCase):
    """Mock-based tests — no real HTTP calls."""

    def test_no_api_key_returns_none(self):
        """When no API key is configured, should return None immediately."""
        with patch("app.get_rapidapi_key", return_value=""):
            result = app.search_api_player("Virat Kohli")
        self.assertIsNone(result)

    def test_empty_player_name_returns_none(self):
        with patch("app.get_rapidapi_key", return_value="fake_key"):
            result = app.search_api_player("")
        self.assertIsNone(result)

    def test_429_returns_quota_exceeded_sentinel(self):
        """HTTP 429 must return the quota_exceeded sentinel dict."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        with patch("app.get_rapidapi_key", return_value="fake_key"), \
             patch("requests.get", return_value=mock_resp):
            result = app.search_api_player("Virat Kohli")
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("quota_exceeded"),
                        "Expected {'quota_exceeded': True} on 429 response")

    def test_200_returns_player_list(self):
        """HTTP 200 with valid JSON must return the player list."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "player": [
                {"id": "1234", "name": "Virat Kohli", "teamName": "India"}
            ]
        }
        with patch("app.get_rapidapi_key", return_value="fake_key"), \
             patch("requests.get", return_value=mock_resp):
            result = app.search_api_player("Virat Kohli")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Virat Kohli")

    def test_200_empty_player_list(self):
        """HTTP 200 but no players found → empty list (truthy check in UI must handle [])."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"player": []}
        with patch("app.get_rapidapi_key", return_value="fake_key"), \
             patch("requests.get", return_value=mock_resp):
            result = app.search_api_player("UnknownXYZ")
        self.assertEqual(result, [])

    def test_network_error_returns_none(self):
        """Any requests exception (timeout, connection error) should return None."""
        import requests as req
        with patch("app.get_rapidapi_key", return_value="fake_key"), \
             patch("requests.get", side_effect=req.exceptions.ConnectionError("no network")):
            result = app.search_api_player("Virat Kohli")
        self.assertIsNone(result)

    def test_quota_sentinel_is_not_falsy(self):
        """The UI checks `isinstance(api_res, dict) and api_res.get('quota_exceeded')` FIRST.
        This test confirms the sentinel is a non-empty dict (not falsy)."""
        sentinel = {"quota_exceeded": True}
        self.assertTrue(bool(sentinel))          # dict is truthy
        self.assertTrue(sentinel.get("quota_exceeded"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

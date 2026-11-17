import datetime
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import update_stats  # noqa: E402


class TestUpdateStats(unittest.TestCase):
    def test_compute_streak_includes_today_and_yesterday_grace(self):
        today = datetime.date(2026, 11, 17)
        weeks = [
            {
                "contributionDays": [
                    {"date": "2026-11-14", "contributionCount": 0},
                    {"date": "2026-11-15", "contributionCount": 3},
                    {"date": "2026-11-16", "contributionCount": 2},
                    {"date": "2026-11-17", "contributionCount": 1},
                ]
            }
        ]
        self.assertEqual(update_stats.compute_streak(weeks, today), 3)

        # Today has 0 commits yet, yesterday had commits -> streak still counts
        weeks[0]["contributionDays"][3]["contributionCount"] = 0
        self.assertEqual(update_stats.compute_streak(weeks, today), 2)

        # Neither today nor yesterday has commits -> streak is 0
        weeks[0]["contributionDays"][2]["contributionCount"] = 0
        self.assertEqual(update_stats.compute_streak(weeks, today), 0)

    def test_compute_streak_handles_empty(self):
        self.assertEqual(update_stats.compute_streak([], datetime.date(2026, 11, 17)), 0)

    def test_aggregate_languages_top_four_plus_other(self):
        repo_langs = [
            {"Python": 5000, "C++": 3000, "Rust": 1000},
            {"Python": 1000, "CMake": 500, "Shell": 300, "Dockerfile": 200},
        ]
        result = update_stats.aggregate_languages(repo_langs)
        names = [item["name"] for item in result]
        self.assertEqual(names, ["Python", "C++", "Rust", "CMake", "Other"])
        total_pct = sum(item["percent"] for item in result)
        self.assertAlmostEqual(total_pct, 100.0, places=1)
        self.assertEqual(result[0]["percent"], 54.5)

    def test_aggregate_languages_handles_empty(self):
        self.assertEqual(update_stats.aggregate_languages([]), [])

    def test_render_stats_svg_is_valid_xml_and_escapes_content(self):
        stats = {
            "username": "Valmor<lee>&",
            "updated_at": "2026-11-17",
            "commits_1y": 512,
            "repos": 8,
            "streak_days": 14,
            "stars": 42,
            "languages": [
                {"name": "Python", "percent": 45.0, "color": "#7aa2f7"},
                {"name": "C++", "percent": 35.0, "color": "#f7768e"},
                {"name": "Rust&Go", "percent": 20.0, "color": "#e0af68"},
            ],
        }
        svg = update_stats.render_stats_svg(stats)
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn("telemetry://github.com/Valmor&lt;lee&gt;&amp;", svg)
        self.assertIn("512", svg)
        self.assertIn("14d", svg)
        self.assertIn("Rust&amp;Go", svg)


if __name__ == "__main__":
    unittest.main()

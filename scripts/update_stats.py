#!/usr/bin/env python3
"""Fetch GitHub telemetry for a user and render a Tokyo Night Bento SVG card."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

PALETTE = ("#7aa2f7", "#f7768e", "#e0af68", "#73daca", "#bb9af7")
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"

GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
    repositories(
      first: 100
      ownerAffiliations: OWNER
      isFork: false
      orderBy: {field: PUSHED_AT, direction: DESC}
    ) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
            }
          }
        }
      }
    }
  }
}
"""


def compute_streak(weeks: list[dict[str, Any]], today: datetime.date | None = None) -> int:
    """Return the current consecutive-day contribution streak ending today or yesterday."""
    if not weeks:
        return 0

    current_day = today or datetime.date.today()
    counts_by_date: dict[datetime.date, int] = {}
    for week in weeks:
        for day in week.get("contributionDays", []):
            raw_date = day.get("date")
            if not raw_date:
                continue
            parsed = datetime.date.fromisoformat(raw_date)
            counts_by_date[parsed] = int(day.get("contributionCount", 0))

    if not counts_by_date:
        return 0

    cursor = current_day
    if counts_by_date.get(cursor, 0) <= 0:
        cursor = current_day - datetime.timedelta(days=1)
        if counts_by_date.get(cursor, 0) <= 0:
            return 0

    streak = 0
    while counts_by_date.get(cursor, 0) > 0:
        streak += 1
        cursor -= datetime.timedelta(days=1)
    return streak


def aggregate_languages(repo_languages: list[dict[str, int]]) -> list[dict[str, Any]]:
    """Aggregate language bytes across repositories into top 4 languages plus Other."""
    totals: dict[str, int] = {}
    for lang_map in repo_languages:
        for name, byte_count in lang_map.items():
            if byte_count > 0:
                totals[name] = totals.get(name, 0) + int(byte_count)

    grand_total = sum(totals.values())
    if grand_total <= 0:
        return []

    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    buckets = list(ranked[:4])
    other_bytes = sum(size for _, size in ranked[4:])
    if other_bytes > 0:
        buckets.append(("Other", other_bytes))

    raw_tenths = [(size / grand_total) * 1000.0 for _, size in buckets]
    floored = [int(val) for val in raw_tenths]
    remainder = 1000 - sum(floored)
    order = sorted(range(len(buckets)), key=lambda i: -(raw_tenths[i] - floored[i]))
    for i in order[:remainder]:
        floored[i] += 1

    result: list[dict[str, Any]] = []
    for idx, (name, _) in enumerate(buckets):
        result.append(
            {
                "name": name,
                "percent": floored[idx] / 10.0,
                "color": PALETTE[idx % len(PALETTE)],
            }
        )
    return result


def fetch_github_stats(username: str, token: str) -> dict[str, Any]:
    """Query GitHub GraphQL API for contribution and repository metrics."""
    payload = json.dumps({"query": GRAPHQL_QUERY, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Valmorlee-Profile-Stats",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    if body.get("errors"):
        raise RuntimeError(f"GitHub GraphQL errors: {body['errors']}")

    user = body["data"]["user"]
    contrib = user["contributionsCollection"]
    commits_1y = int(contrib.get("totalCommitContributions", 0)) + int(
        contrib.get("restrictedContributionsCount", 0)
    )
    weeks = contrib.get("contributionCalendar", {}).get("weeks", [])
    streak_days = compute_streak(weeks, datetime.datetime.now(datetime.timezone.utc).date())

    repos_conn = user["repositories"]
    repo_nodes = repos_conn.get("nodes", [])
    stars = sum(int(node.get("stargazerCount", 0)) for node in repo_nodes)

    repo_langs: list[dict[str, int]] = []
    for node in repo_nodes:
        lang_map: dict[str, int] = {}
        for edge in node.get("languages", {}).get("edges", []):
            lang_name = edge.get("node", {}).get("name")
            size = int(edge.get("size", 0))
            if lang_name and size > 0:
                lang_map[lang_name] = size
        if lang_map:
            repo_langs.append(lang_map)

    return {
        "username": username,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        "commits_1y": commits_1y,
        "repos": int(repos_conn.get("totalCount", len(repo_nodes))),
        "streak_days": streak_days,
        "stars": stars,
        "languages": aggregate_languages(repo_langs),
    }


def render_stats_svg(stats: dict[str, Any]) -> str:
    """Render a Tokyo Night Bento SVG telemetry card from aggregated GitHub stats."""
    username = escape(str(stats["username"]))
    updated_at = escape(str(stats["updated_at"]))

    metrics = [
        ("COMMITS (1Y)", str(stats["commits_1y"]), "#7aa2f7"),
        ("REPOSITORIES", str(stats["repos"]), "#73daca"),
        ("CURRENT STREAK", f"{stats['streak_days']}d", "#e0af68"),
        ("TOTAL STARS", str(stats["stars"]), "#bb9af7"),
    ]

    tiles_svg: list[str] = []
    tile_width = 170
    tile_gap = 13
    for idx, (label, value, color) in enumerate(metrics):
        x = 20 + idx * (tile_width + tile_gap)
        tiles_svg.append(
            f'  <rect x="{x}" y="52" width="{tile_width}" height="54" rx="6" fill="#16161e" stroke="#292e42"/>\n'
            f'  <text x="{x + 12}" y="71" fill="#565f89" font-family="{FONT_MONO}" font-size="10">{escape(label)}</text>\n'
            f'  <text x="{x + 12}" y="95" fill="{color}" font-family="{FONT_MONO}" font-size="20" font-weight="700">{escape(value)}</text>'
        )

    bar_width = 720
    bar_x = 20
    languages = stats.get("languages") or []
    bar_segments: list[str] = []
    legend_items: list[str] = []

    if languages:
        cursor_x = float(bar_x)
        col_step = max(120, bar_width // max(1, len(languages)))
        for idx, lang in enumerate(languages):
            pct = max(0.0, float(lang["percent"]))
            seg_w = (bar_x + bar_width - cursor_x) if idx == len(languages) - 1 else (bar_width * (pct / 100.0))
            if seg_w > 0:
                bar_segments.append(
                    f'    <rect x="{cursor_x:.1f}" y="120" width="{seg_w:.1f}" height="8" fill="{escape(lang["color"])}"/>'
                )
            cursor_x += seg_w

            label_text = f"{lang['name']} {pct:.1f}%"
            legend_x = bar_x + idx * col_step
            legend_items.append(
                f'  <circle cx="{legend_x + 4}" cy="142" r="3.5" fill="{escape(lang["color"])}"/>\n'
                f'  <text x="{legend_x + 12}" y="145" fill="#a9b1d6" font-family="{FONT_MONO}" font-size="10">{escape(label_text)}</text>'
            )
    else:
        bar_segments.append(f'    <rect x="{bar_x}" y="120" width="{bar_width}" height="8" fill="#292e42"/>')
        legend_items.append(
            f'  <text x="20" y="145" fill="#565f89" font-family="{FONT_MONO}" font-size="10">No language data available yet</text>'
        )

    return (
        f'<svg viewBox="0 0 760 164" width="760" height="164" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub telemetry for {username}">\n'
        f'  <defs>\n'
        f'    <clipPath id="lang-bar-clip">\n'
        f'      <rect x="20" y="120" width="720" height="8" rx="4"/>\n'
        f'    </clipPath>\n'
        f'  </defs>\n'
        f'  <rect x="0.5" y="0.5" width="759" height="163" rx="10" fill="#1a1b27" stroke="#292e42"/>\n'
        f'  <text x="20" y="28" fill="#7aa2f7" font-family="{FONT_MONO}" font-size="12" font-weight="700">telemetry://github.com/{username}</text>\n'
        f'  <text x="740" y="28" text-anchor="end" fill="#565f89" font-family="{FONT_MONO}" font-size="10.5">updated {updated_at}</text>\n'
        f'  <line x1="20" y1="40" x2="740" y2="40" stroke="#292e42" stroke-width="1"/>\n'
        + "\n".join(tiles_svg)
        + "\n"
        f'  <rect x="20" y="120" width="720" height="8" rx="4" fill="#16161e"/>\n'
        f'  <g clip-path="url(#lang-bar-clip)">\n'
        + "\n".join(bar_segments)
        + "\n  </g>\n"
        + "\n".join(legend_items)
        + "\n</svg>\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate GitHub telemetry SVG card.")
    parser.add_argument("--username", default=os.environ.get("GITHUB_USERNAME", "Valmorlee"))
    parser.add_argument("--output", default="assets/github-stats.svg")
    args = parser.parse_args()

    token = os.environ.get("GH_STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN or GH_STATS_TOKEN environment variable is required.", file=sys.stderr)
        return 1

    stats = fetch_github_stats(args.username, token)
    svg = render_stats_svg(stats)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    print(f"Wrote {output_path} for {args.username} ({stats['commits_1y']} commits, {stats['repos']} repos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

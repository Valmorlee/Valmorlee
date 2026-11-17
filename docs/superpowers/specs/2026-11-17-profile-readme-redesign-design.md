# Valmorlee GitHub Profile README Redesign Design Spec

**Date:** 2026-11-17  
**Target Repository:** `Valmorlee/Valmorlee` (GitHub Profile Repository)  
**Visual Theme:** Tokyo Night (`#0d1117` canvas, `#1a1b27` card surface, `#16161e` inset/titlebar, `#292e42` border, `#7aa2f7` / `#73daca` / `#bb9af7` / `#e0af68` accents)

---

## 1. Goals & Problem Statement

Replace visually underwhelming modules in `README.md` with cohesive, popular, high-craft developer profile components:
1. Replace plain `<h1>` + mismatched `capsule-render` default font with embedded-font geek typography (`Silkscreen` + `JetBrains Mono` + `Fira Code`), removing the header badge and view-counter bar.
2. Replace the raw `<pre>` block in `About` with a repository-hosted Tokyo Night terminal SVG card (`assets/focus.svg`).
3. Replace 19 monotonous dark `shields.io` badges in `Stack` with `go-skill-icons` rounded icon matrices plus clean inline monospace tags for specialized runtimes not in `go-skill-icons`.
4. Replace the plain Markdown `Projects` table with a symmetrical `2×3` Bento grid of custom Tokyo Night SVG project cards (`assets/projects/*.svg`), keeping public repositories clickable.
5. Replace ugly third-party GitHub stats cards (`ghstats.dev`, etc.) with a unified GitHub Actions-generated telemetry Bento SVG (`assets/github-stats.svg`) paired with `Platane/snk` animated contribution snake (`output` branch, light/dark adaptive via `<picture>`).

---

## 2. File Architecture

```text
.
├── README.md                                  # Redesigned profile entrypoint
├── assets/
│   ├── focus.svg                              # Static Terminal focus.toml card
│   ├── github-stats.svg                       # Auto-updated daily telemetry card
│   └── projects/
│       ├── hyxon.svg                          # Private project Bento card
│       ├── deus-vision-rm.svg                 # Private project Bento card
│       ├── omniaven-v2.svg                    # Private project Bento card
│       ├── rm-yolo-onnx.svg                   # Public demo Bento card (linked)
│       ├── sys-csroom.svg                     # Public project Bento card (linked)
│       └── more-experiments.svg               # 6th card to keep 2×3 symmetry (linked)
├── scripts/
│   └── update_stats.py                        # Zero-dependency Python 3 script fetching GitHub GraphQL/REST & rendering assets/github-stats.svg
├── tests/
│   └── test_update_stats.py                   # Unit tests for stats aggregation, streak calculation, and SVG validity
├── .github/
│   └── workflows/
│       └── profile.yml                        # Daily cron + push/dispatch workflow updating stats SVG & Platane/snk snake
└── docs/superpowers/specs/
    └── 2026-11-17-profile-readme-redesign-design.md
```

---

## 3. Section-by-Section Specification

### 3.1 Header (`H3` + `JetBrains Mono` Subtitle, No Badge Bar)
- Centered layout with zero `shields.io` badges or view counters.
- **Title**: `readme-typing-svg.demolab.com` with `font=Silkscreen`, `weight=700`, `size=38`, `color=7AA2F7`, `pause=60000`, `lines=VALMORLEE`.
- **Subtitle**: `readme-typing-svg.demolab.com` with `font=JetBrains+Mono`, `weight=600`, `size=15`, `color=A9B1D6`, `duration=800`, `pause=60000`, `lines=CS+student+%40+ZJUT+%C2%B7+Robotics+AI+%26+Infra+Rookie`.
- **CLI Ticker**: `readme-typing-svg.demolab.com` with `font=Fira+Code`, `weight=500`, `size=15`, `color=73DACA`, `pause=1200`, cycling:
  1. `$ whoami → ZJUT CS | ArcMeow-Lab Tech Lead`
  2. `$ vision → C++20 / CUDA / TensorRT FP16`
  3. `$ agents → Rust / Python / LangGraph / RAG`

### 3.2 About
- Two-column layout (`<table>` with clean `width="58%"` left text and `width="42%"` right SVG).
- **Left cell**: Concise bio bullets (ZJUT CS, Vision Leader @ ZJUTDeus RoboMaster 2027, Tech Lead @ ArcMeow-Lab, focus areas, and fun fact).
- **Right cell**: `<img src="./assets/focus.svg" alt="Current Focus Terminal Card" width="100%" />`.
- `assets/focus.svg` (`420×176` viewBox): macOS traffic lights (`#f7768e`, `#e0af68`, `#9ece6a`), title `valmorlee@zjut — focus.toml`, TOML key-value pairs for `vision`, `backend`, `agents`, `robotics`, and status comment. Uses system monospace font stack (`ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`) so GitHub's SVG renderer displays crisp typography without external font requests.

### 3.3 Tech Stack
- Two centered rows via `go-skill-icons.vercel.app`:
  - Row 1 (`9` icons): `py,cpp,rust,java,go,cuda,pytorch,opencv,ros` (`theme=dark`)
  - Row 2 (`8` icons): `langchain,fastapi,neo4j,redis,docker,cmake,linux,git` (`theme=dark`)
- Below the icons, a centered inline monospace pill line for runtimes/libraries absent from `go-skill-icons`:
  ``Also working with: `TensorRT` · `ONNX Runtime` · `LangGraph` · `Qdrant` · `Eigen3` ``

### 3.4 Projects (`2×3` Symmetrical Bento Grid)
- Rendered as a 3-row × 2-column HTML `<table>` containing `6` equal-aspect (`380×126` viewBox) SVG cards in `assets/projects/`:
  1. **Hyxon** (`Private`, Python / `#3572A5` — `FastAPI · LangGraph · Neo4j · Redis`)
  2. **Deus-Vision-RM** (`Private`, C++20 / `#f34b7d` — `CUDA · TensorRT · OpenCV · Eigen3`)
  3. **OmniAven-v2** (`Private`, Rust / `#dea584` — `Axum · Tokio · Qdrant · ONNX`)
  4. **RM_yoloONNX** (`Demo`, C++ / `#f34b7d` — `ONNX Runtime · YOLO`, wrapped in `<a href="https://github.com/Valmorlee/RM_yoloONNX">`)
  5. **Sys_CSRoom** (`Public`, C++ / `#f34b7d` — `FTXUI · TUI`, wrapped in `<a href="https://github.com/Valmorlee/Sys_CSRoom">`)
  6. **ArcMeow-Lab & More** (`Explore` dashed card linking to `https://github.com/Valmorlee?tab=repositories`)
- Card structure: Tokyo Night `#1a1b27` background, `#292e42` 1px stroke, colored status dot, bold project title, pill badge (`Private` / `Demo` / `Public` / `Explore`), 2-line description, primary language dot + label, and stack summary.

### 3.5 Telemetry & Activity (`S1` + Snake)
1. **Unified Telemetry Card (`assets/github-stats.svg`)**:
   - Dimensions: `760×160` viewBox, `#1a1b27` card background, `#292e42` border, `#16161e` inner metric tiles.
   - Header: `telemetry://github.com/Valmorlee` (left) + `updated YYYY-MM-DD` (right).
   - 4 metric tiles:
     - `COMMITS (1Y)` — from GraphQL `contributionsCollection.totalCommitContributions + restrictedContributionsCount`
     - `REPOSITORIES` — accessible non-fork repositories (`public` with default `GITHUB_TOKEN`; `public + private` when `GH_STATS_TOKEN` is configured)
     - `CURRENT STREAK` — computed from GraphQL `contributionCalendar.weeks`
     - `TOTAL STARS` — summed `stargazerCount` across owned repositories
   - Bottom stacked horizontal bar + legend: Top 4 languages by byte size across owned non-fork repositories, plus an `Other` segment when additional languages exist.
2. **Contribution Snake (`Platane/snk`)**:
   - Generated by `.github/workflows/profile.yml` to the `output` branch (`github-contribution-grid-snake-dark.svg` & `github-contribution-grid-snake.svg`).
   - Embedded in `README.md` using GitHub `<picture>` (`prefers-color-scheme: dark` vs light) referencing `https://raw.githubusercontent.com/Valmorlee/Valmorlee/output/...`.

---

## 4. Automation & Reliability Details

- **`scripts/update_stats.py`**:
  - Uses Python 3 standard library only (`urllib.request`, `json`, `os`, `datetime`, `xml.sax.saxutils`) — zero pip dependencies.
  - Reads `GITHUB_TOKEN` (from `secrets.GH_STATS_TOKEN || secrets.GITHUB_TOKEN` in CI) and `GITHUB_USERNAME` (defaults to `Valmorlee`).
  - Exposes pure functions `compute_streak(weeks, today)`, `aggregate_languages(repos)`, and `render_stats_svg(stats)` so all logic is unit-testable offline.
  - Initial `assets/github-stats.svg` is generated from live public GitHub REST data on creation (and immediately refreshed once the first workflow run completes).
- **`.github/workflows/profile.yml`**:
  - Triggers: daily `cron: "0 18 * * *"` (02:00 CST), `workflow_dispatch`, and `push` to `main` (ignoring `assets/github-stats.svg` to prevent self-trigger loops).
  - Permissions: `contents: write`.
  - Steps:
    1. Checkout `main`
    2. Run `python3 scripts/update_stats.py` and commit/push `assets/github-stats.svg` if modified
    3. Run `Platane/snk@v3` and deploy `github-contribution-grid-snake*.svg` to `output` branch via `crazy-max/ghaction-github-pages@v4`.

---

## 5. Verification Plan

1. Validate all generated SVGs (`assets/focus.svg`, `assets/projects/*.svg`, `assets/github-stats.svg`) parse cleanly with `xml.etree.ElementTree`.
2. Run `python3 -m unittest discover -s tests` to verify `scripts/update_stats.py` streak calculation, language aggregation, XML escaping, and SVG rendering.
3. Visually inspect the rendered `README.md` layout and verify all external badge/SVG URLs return HTTP 200 without broken images.

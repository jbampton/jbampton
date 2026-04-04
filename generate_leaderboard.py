#!/usr/bin/env python3
"""Generate a contribution leaderboard README for jbampton's GitHub profile.

Fetches contribution data from the GitHub Search API and generates a markdown
leaderboard showing all repositories contributed to, with detailed statistics
including commit counts, streaks, points, and badges.

Usage:
    GITHUB_TOKEN=<token> python generate_leaderboard.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GITHUB_USERNAME: str = "jbampton"
GITHUB_API_URL: str = "https://api.github.com"
README_PATH: str = "README.md"
MAX_SEARCH_PAGES: int = 10  # GitHub Search API caps at 1 000 results
PER_PAGE: int = 100

# Points
POINTS_PER_COMMIT: int = 1
POINTS_PER_COAUTHORED: int = 3
POINTS_STREAK_BONUS_DAYS: int = 10
POINTS_STREAK_BONUS: int = 5
POINTS_CENTURY_BONUS: int = 10
POINTS_FIVE_HUNDRED_BONUS: int = 25
POINTS_THOUSAND_BONUS: int = 50

# Badge tiers (inclusive bounds)
BADGE_TIERS: list[tuple[str, int, float]] = [
    ("🌱 Seedling", 1, 4),
    ("🌿 Growing", 5, 19),
    ("🌳 Rooted", 20, 49),
    ("🔥 On Fire", 50, 99),
    ("💎 Diamond", 100, 499),
    ("🌟 Super Star", 500, 999),
    ("👑 Legend", 1000, float("inf")),
]


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------
@dataclass
class RepoContribution:
    """Contribution statistics for a single repository."""

    repo_name: str
    repo_url: str
    total_commits: int = 0
    authored_commits: int = 0
    coauthored_commits: int = 0
    first_commit_date: str | None = None
    commit_dates: list[str] = field(default_factory=list)

    # -- Derived Properties -------------------------------------------------

    @property
    def badge(self) -> str:
        """Tier badge based on total commit count."""
        for name, low, high in BADGE_TIERS:
            if low <= self.total_commits <= high:
                return name
        return "🌱 Seedling"

    @property
    def streak(self) -> int:
        """Longest streak of consecutive calendar days with commits."""
        if not self.commit_dates:
            return 0
        unique_days = sorted({d[:10] for d in self.commit_dates})
        if len(unique_days) <= 1:
            return len(unique_days)
        best = current = 1
        for i in range(1, len(unique_days)):
            prev = datetime.strptime(unique_days[i - 1], "%Y-%m-%d")
            curr = datetime.strptime(unique_days[i], "%Y-%m-%d")
            if (curr - prev).days == 1:
                current += 1
                best = max(best, current)
            else:
                current = 1
        return best

    @property
    def active_streak(self) -> int:
        """Current active streak ending today or yesterday (UTC)."""
        if not self.commit_dates:
            return 0
        unique_days = sorted({d[:10] for d in self.commit_dates}, reverse=True)
        now_utc = datetime.now(timezone.utc)
        today = now_utc.strftime("%Y-%m-%d")
        yesterday = (now_utc - timedelta(days=1)).strftime("%Y-%m-%d")
        if unique_days[0] not in (today, yesterday):
            return 0
        streak = 1
        for i in range(1, len(unique_days)):
            prev = datetime.strptime(unique_days[i - 1], "%Y-%m-%d")
            curr = datetime.strptime(unique_days[i], "%Y-%m-%d")
            if (prev - curr).days == 1:
                streak += 1
            else:
                break
        return streak

    @property
    def points(self) -> int:
        """Score based on commits, streaks, and milestones."""
        pts = self.authored_commits * POINTS_PER_COMMIT
        pts += self.coauthored_commits * POINTS_PER_COAUTHORED
        pts += (self.streak // POINTS_STREAK_BONUS_DAYS) * POINTS_STREAK_BONUS
        if self.total_commits >= 1000:
            pts += POINTS_THOUSAND_BONUS
        elif self.total_commits >= 500:
            pts += POINTS_FIVE_HUNDRED_BONUS
        elif self.total_commits >= 100:
            pts += POINTS_CENTURY_BONUS
        return pts

    @property
    def description(self) -> str:
        """Auto-generated flavour text based on contribution level."""
        if self.total_commits >= 1000:
            return "🏰 Legendary contributor — a true pillar of this project"
        if self.total_commits >= 500:
            return "⚔️ Elite warrior — battle-tested and unstoppable"
        if self.total_commits >= 100:
            return "🛡️ Centurion — committed and consistent force"
        if self.total_commits >= 50:
            return "🚀 Rising star — making serious impact"
        if self.total_commits >= 20:
            return "🎯 Sharpshooter — precision contributions"
        if self.total_commits >= 5:
            return "🌿 Budding contributor — growing with the project"
        return "🌱 First steps — every journey begins here"

    @property
    def activity_emoji(self) -> str:
        """Emoji indicating whether the streak is currently active."""
        if self.active_streak >= 7:
            return "⚡"
        if self.active_streak >= 1:
            return "✅"
        return "💤"


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------
def _get_token() -> str:
    """Read ``GITHUB_TOKEN`` from the environment."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(
            "Warning: GITHUB_TOKEN not set — API rate limits will be very low.",
            file=sys.stderr,
        )
    return token


def _api_request(url: str, token: str) -> tuple[dict | list, dict]:
    """Authenticated GitHub API request with a single rate-limit retry."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{GITHUB_USERNAME}-leaderboard",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            reset = int(exc.headers.get("X-RateLimit-Reset", "0"))
            wait = max(reset - int(time.time()), 1)
            print(f"Rate-limited. Sleeping {min(wait, 60)}s …", file=sys.stderr)
            time.sleep(min(wait, 60))
            with urllib.request.urlopen(req) as resp:
                return json.load(resp), dict(resp.headers)
        raise


def _has_next_page(headers: dict) -> bool:
    """Return *True* if the ``Link`` header contains a ``rel="next"`` link."""
    for part in headers.get("Link", "").split(","):
        if 'rel="next"' in part:
            return True
    return False


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------
def _record_commit(
    repos: dict[str, RepoContribution],
    item: dict,
    *,
    is_authored: bool,
) -> None:
    """Add a single commit record to the *repos* dictionary."""
    repo_data = item.get("repository", {})
    repo_full = repo_data.get("full_name", "unknown/unknown")
    repo_html = repo_data.get(
        "html_url", f"https://github.com/{repo_full}"
    )
    commit_info = item.get("commit", {})
    date_key = "author" if is_authored else "committer"
    commit_date = commit_info.get(date_key, {}).get("date", "")

    if repo_full not in repos:
        repos[repo_full] = RepoContribution(
            repo_name=repo_full, repo_url=repo_html
        )

    entry = repos[repo_full]
    entry.total_commits += 1
    if is_authored:
        entry.authored_commits += 1
    else:
        entry.coauthored_commits += 1

    if commit_date:
        entry.commit_dates.append(commit_date)
        if entry.first_commit_date is None or commit_date < entry.first_commit_date:
            entry.first_commit_date = commit_date


def fetch_commits(
    token: str,
    query: str,
    *,
    is_authored: bool,
    repos: dict[str, RepoContribution],
) -> None:
    """Page through the GitHub Search commits API for *query*."""
    base = (
        f"{GITHUB_API_URL}/search/commits"
        f"?q={query}&sort=author-date&order=asc&per_page={PER_PAGE}"
    )
    for page in range(1, MAX_SEARCH_PAGES + 1):
        url = f"{base}&page={page}"
        label = "authored" if is_authored else "co-authored"
        print(f"Fetching {label} commits — page {page} …", file=sys.stderr)
        data, headers = _api_request(url, token)

        for item in data.get("items", []):
            _record_commit(repos, item, is_authored=is_authored)

        if not data.get("items") or not _has_next_page(headers):
            break
        time.sleep(1)  # stay well within rate limits


# ---------------------------------------------------------------------------
# Profile-level badges
# ---------------------------------------------------------------------------
def compute_profile_badges(repos: dict[str, RepoContribution]) -> list[str]:
    """Derive global achievement badges from aggregate stats."""
    badges: list[str] = []
    total_commits = sum(r.total_commits for r in repos.values())
    total_repos = len(repos)
    total_coauthored = sum(r.coauthored_commits for r in repos.values())
    max_streak = max((r.streak for r in repos.values()), default=0)
    max_active = max((r.active_streak for r in repos.values()), default=0)

    if total_repos >= 100:
        badges.append("🌍 **Globe Trotter** — Contributed to 100+ repos")
    elif total_repos >= 50:
        badges.append("🎯 **Sharpshooter** — Contributed to 50+ repos")
    if total_commits >= 5000:
        badges.append("👑 **Legendary** — 5,000+ total commits")
    elif total_commits >= 1000:
        badges.append("🏆 **Grand Master** — 1,000+ total commits")
    if total_coauthored >= 50:
        badges.append("💪 **Collaboration King** — 50+ co-authored commits")
    elif total_coauthored >= 10:
        badges.append("🤝 **Team Player** — 10+ co-authored commits")
    if max_streak >= 30:
        badges.append("⚡ **Streak Master** — 30+ day streak")
    if max_active >= 7:
        badges.append("🦾 **Iron Will** — 7+ day active streak")
    if any(r.total_commits >= 1000 for r in repos.values()):
        badges.append("🌟 **Millennium Force** — 1,000+ commits in a single repo")
    elif any(r.total_commits >= 100 for r in repos.values()):
        badges.append("💎 **Century Club** — 100+ commits in a single repo")

    if not badges:
        badges.append("🌱 **Explorer** — The journey has begun!")
    return badges


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------
def _overview_table(repos: dict[str, RepoContribution]) -> str:
    total_commits = sum(r.total_commits for r in repos.values())
    total_authored = sum(r.authored_commits for r in repos.values())
    total_coauthored = sum(r.coauthored_commits for r in repos.values())
    total_repos = len(repos)
    total_points = sum(r.points for r in repos.values())
    max_streak = max((r.streak for r in repos.values()), default=0)
    max_active = max((r.active_streak for r in repos.values()), default=0)

    return (
        "| Metric | Value |\n"
        "|--------|-------|\n"
        f"| 📦 Total Repos Contributed | **{total_repos}** |\n"
        f"| 📝 Total Commits | **{total_commits:,}** |\n"
        f"| ✍️ Authored Commits | **{total_authored:,}** |\n"
        f"| 🤝 Co-authored Commits | **{total_coauthored:,}** |\n"
        f"| 🔥 Longest Streak | **{max_streak} days** |\n"
        f"| ⚡ Best Active Streak | **{max_active} days** |\n"
        f"| 🎯 Total Points | **{total_points:,}** |\n"
    )


def _leaderboard_table(repos: dict[str, RepoContribution]) -> str:
    sorted_repos = sorted(
        repos.values(), key=lambda r: r.total_commits, reverse=True
    )
    lines = [
        (
            "| # | 🏷️ Repository | 📝 Total | ✍️ Authored | 🤝 Co-authored "
            "| 📅 First Commit | 🔥 Streak | ⚡ Active | 🎯 Points "
            "| 🏅 Badge | 💬 Description |"
        ),
        (
            "|---|--------------|----------|------------|----------------"
            "|-----------------|-----------|----------|----------"
            "|---------|-------------|"
        ),
    ]
    for rank, r in enumerate(sorted_repos, 1):
        first = r.first_commit_date[:10] if r.first_commit_date else "N/A"
        lines.append(
            f"| {rank} "
            f"| [{r.repo_name}]({r.repo_url}) "
            f"| {r.total_commits:,} "
            f"| {r.authored_commits:,} "
            f"| {r.coauthored_commits:,} "
            f"| {first} "
            f"| {r.streak} days "
            f"| {r.activity_emoji} {r.active_streak} days "
            f"| {r.points:,} "
            f"| {r.badge} "
            f"| {r.description} |"
        )
    return "\n".join(lines)


def _legend() -> str:
    return """\
### 📖 Legend

| Symbol | Meaning |
|--------|---------|
| 📝 Total | Total number of commits (authored + co-authored) |
| ✍️ Authored | Commits directly authored by jbampton |
| 🤝 Co-authored | Commits where jbampton was the committer but not the primary author |
| 📅 First Commit | Date of the earliest commit to the repository |
| 🔥 Streak | Longest run of consecutive calendar days with at least one commit |
| ⚡ Active | Current streak — consecutive days ending today or yesterday (UTC) |
| 🎯 Points | Weighted score combining commits, streaks, and milestone bonuses |
| 🏅 Badge | Tier badge awarded based on total commits to the repo |
| 💬 Description | Auto-generated flavour text describing the contribution level |

### 🎯 Points System

| Action | Points |
|--------|--------|
| Each authored commit | **+1** |
| Each co-authored commit | **+3** (collaboration bonus) |
| Every 10-day streak | **+5** |
| 100+ commits in a repo | **+10** milestone bonus |
| 500+ commits in a repo | **+25** milestone bonus |
| 1,000+ commits in a repo | **+50** milestone bonus |

### 🏅 Badge Tiers

| Badge | Commits |
|-------|---------|
| 🌱 Seedling | 1 – 4 |
| 🌿 Growing | 5 – 19 |
| 🌳 Rooted | 20 – 49 |
| 🔥 On Fire | 50 – 99 |
| 💎 Diamond | 100 – 499 |
| 🌟 Super Star | 500 – 999 |
| 👑 Legend | 1,000 + |
"""


def generate_readme(repos: dict[str, RepoContribution]) -> str:
    """Compose the full README content."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    badges = compute_profile_badges(repos)
    badge_md = "\n".join(f"- {b}" for b in badges)

    return f"""\
<!-- start-data -->
<div align="center">
  <h1>🏆 jbampton's Open Source Contribution Leaderboard 🏆</h1>
  <p><em>🤖 Auto-updated daily at 4:17 AM UTC via GitHub Actions</em></p>
  <p><em>Last updated: {now}</em></p>
  <p>
    <a href="https://github.com/jbampton">
      <img src="https://img.shields.io/badge/GitHub-jbampton-181717?style=for-the-badge&logo=github" alt="GitHub Profile">
    </a>
    <a href="https://github.com/sponsors/jbampton">
      <img src="https://img.shields.io/badge/Sponsor-❤️-ea4aaa?style=for-the-badge&logo=github-sponsors" alt="Sponsor">
    </a>
  </p>
</div>

---

<div align="center">

## 📊 Stats Overview

{_overview_table(repos)}
</div>

---

<div align="center">

## 🏅 Profile Badges

{badge_md}

</div>

---

## 🏆 Contribution Leaderboard

{_leaderboard_table(repos)}

---

{_legend()}

---

<div align="center">
  <p><em>🤖 Generated with ❤️ by <a href="https://github.com/jbampton/jbampton">jbampton/jbampton</a></em></p>
  <p><em>Data sourced from the GitHub Search API · Limited to the 1,000 most recent commits per category</em></p>
</div>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Fetch data and regenerate ``README.md``."""
    token = _get_token()

    print("🚀 Fetching authored commits …", file=sys.stderr)
    repos: dict[str, RepoContribution] = {}
    fetch_commits(
        token,
        f"author:{GITHUB_USERNAME}",
        is_authored=True,
        repos=repos,
    )

    print("🚀 Fetching co-authored commits …", file=sys.stderr)
    fetch_commits(
        token,
        f"committer:{GITHUB_USERNAME}+-author:{GITHUB_USERNAME}",
        is_authored=False,
        repos=repos,
    )

    if not repos:
        print("⚠️  No contribution data found.", file=sys.stderr)
        sys.exit(1)

    print(
        f"📊 Found contributions to {len(repos)} repositories.",
        file=sys.stderr,
    )

    with open(README_PATH, "w", encoding="utf-8") as fh:
        fh.write(generate_readme(repos))

    print("✅ README.md updated successfully!", file=sys.stderr)


if __name__ == "__main__":
    main()

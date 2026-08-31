#!/usr/bin/env python3
"""Generate a dual-timezone (UTC vs UTC+4) commit-hour bar chart as a static SVG."""
import os

import matplotlib
import requests

matplotlib.use("Agg")
import matplotlib.pyplot as plt

USERNAME = "Momad-Y"
LOCAL_OFFSET = 4
LOCAL_LABEL = "UTC+4 (Dubai)"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
API = "https://api.github.com"
OUTPUT_PATH = "profile-summary-card-output/custom/commits-utc-vs-local.svg"


def get_repos():
    repos, url = [], f"{API}/users/{USERNAME}/repos?per_page=100&type=owner"
    while url:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        repos.extend(repo["name"] for repo in r.json() if not repo["fork"])
        url = r.links.get("next", {}).get("url")
    return repos


def get_commit_hours(repo):
    hours = []
    url = f"{API}/repos/{USERNAME}/{repo}/commits?author={USERNAME}&per_page=100"
    while url:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            break
        for commit in r.json():
            date = commit.get("commit", {}).get("author", {}).get("date")
            if date:
                hours.append(int(date[11:13]))
        url = r.links.get("next", {}).get("url")
    return hours


def main():
    utc_counts = [0] * 24
    for repo in get_repos():
        for hour in get_commit_hours(repo):
            utc_counts[hour] += 1

    local_counts = [0] * 24
    for hour, count in enumerate(utc_counts):
        local_counts[(hour + LOCAL_OFFSET) % 24] += count

    bg = "#1a1b27"
    fg = "#c9cbe0"
    utc_color = "#7aa2f7"
    local_color = "#bb9af7"

    plt.rcParams["svg.fonttype"] = "path"
    fig, ax = plt.subplots(figsize=(7.2, 2.0), dpi=100)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    x = range(24)
    width = 0.4
    ax.bar([i - width / 2 for i in x], utc_counts, width, label="UTC", color=utc_color)
    ax.bar([i + width / 2 for i in x], local_counts, width, label=LOCAL_LABEL, color=local_color)

    ax.set_title("Commits by hour, UTC vs UTC+4 (Dubai)", color=fg, fontsize=11, loc="left")
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlim(-1, 24)
    ax.tick_params(colors=fg, labelsize=7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(fg)
    ax.legend(facecolor=bg, edgecolor=bg, labelcolor=fg, fontsize=7, loc="upper left")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, format="svg", facecolor=bg)


if __name__ == "__main__":
    main()

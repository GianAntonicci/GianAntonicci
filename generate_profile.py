import json
import os
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

USER = "GianAntonicci"
WIDTH = 62
OUT = Path(__file__).resolve().parent / "README.md"


def api(path, token):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def fetch_stats():
    token = os.environ.get("GITHUB_TOKEN")

    user = api(f"/users/{USER}", token)
    repos = []
    page = 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&page={page}", token)
        repos += batch
        if len(batch) < 100:
            break
        page += 1

    commits = api(f"/search/commits?q=author:{USER}&per_page=1", token)["total_count"]
    contributed = api(f"/search/issues?q=author:{USER}+type:pr&per_page=1", token)["total_count"]

    created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - created).days
    years, rem = divmod(days, 365)
    months, days = divmod(rem, 30)

    return {
        "uptime": f"{years} {'ano' if years == 1 else 'anos'}, {months} {'mês' if months == 1 else 'meses'}, "
        f"{days} {'dia' if days == 1 else 'dias'}",
        "repos": str(user["public_repos"]),
        "contrib": str(contributed),
        "stars": str(sum(r["stargazers_count"] for r in repos)),
        "commits": f"{commits:,}",
        "followers": str(user["followers"]),
    }


def entry(key, value, width=WIDTH):
    dots = width - len(key) - len(value) - 5
    return [(". ", "text"), (key + ":", "key"), (" " + "." * dots + " ", "text"), (value, "text")]


def header(title, width=WIDTH):
    return [(title + " ", "text"), ("—" * (width - len(title) - 4) + "-—-", "text")]


def pair(k1, v1, w1, k2, v2, w2):
    left = entry(k1, v1, w1)
    right = entry(k2, v2, w2)
    right[0] = (" | ", "text")
    return left + right


def build(stats):
    blank = [(".", "text")]
    lines = [
        header("gianluca@antonicci"),
        entry("OS", "macOS, Windows, Linux"),
        entry("Uptime", stats["uptime"]),
        entry("Host", "FIAP"),
        entry("Kernel", "Engenharia de Software"),
        entry("IDE", "VSCode"),
        blank,
        entry("Languages.Programming", "Python, JavaScript, C++"),
        entry("Languages.Computer", "HTML, CSS"),
        entry("Languages.Real", "Português, English"),
        blank,
        entry("Hobbies.Software", "Full Stack Web, IA"),
        entry("Hobbies.Hardware", "IoT, Arduino"),
        entry("Hobbies.Creative", "Blender, Fusion 360, Lightburn"),
        blank,
        [("- ", "text")] + header("Contact", WIDTH - 2),
        entry("Email.Personal", "gianluca.antonicci@gmail.com"),
        entry("LinkedIn", "gianluca-antonicci"),
        entry("GitHub", USER),
        blank,
        [("- ", "text")] + header("GitHub Stats", WIDTH - 2),
        pair("Repos", f"{stats['repos']} {{Contributed: {stats['contrib']}}}", 34, "Stars", stats["stars"], 27),
        pair("Commits", stats["commits"], 34, "Followers", stats["followers"], 27),
    ]

    rows = "\n".join(
        "".join(f"<b>{escape(text)}</b>" if kind == "key" else escape(text) for text, kind in parts)
        for parts in lines
    )
    return f"<pre>\n{rows}\n</pre>\n"


if __name__ == "__main__":
    OUT.write_text(build(fetch_stats()), encoding="utf-8")
    print(f"Gerado {OUT}")

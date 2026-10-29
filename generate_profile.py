import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = "GianAntonicci"
README = Path(__file__).resolve().parent / "README.md"


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
        "Uptime": f"{years} {'ano' if years == 1 else 'anos'}, {months} {'mês' if months == 1 else 'meses'}, "
        f"{days} {'dia' if days == 1 else 'dias'}",
        "Repos": f"{user['public_repos']} {{Contributed: {contributed}}}",
        "Stars": str(sum(r["stargazers_count"] for r in repos)),
        "Commits": f"{commits:,}",
        "Followers": str(user["followers"]),
    }


def replace_value(text, key, value):
    # Troca o valor mantendo a largura do segmento (os pontos absorvem a diferença)
    pattern = re.compile(rf"(<b>{re.escape(key)}:</b> )(\.+)( )(.+?)(?=( \| |$))", re.M)

    def sub(m):
        dots = max(len(m.group(2)) + len(m.group(4)) - len(value), 1)
        return f"{m.group(1)}{'.' * dots} {value}"

    return pattern.sub(sub, text, count=1)


if __name__ == "__main__":
    text = README.read_text(encoding="utf-8")
    for key, value in fetch_stats().items():
        text = replace_value(text, key, value)
    README.write_text(text, encoding="utf-8")
    print(f"Atualizado {README}")

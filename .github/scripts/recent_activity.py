"""Rewrite the "Recent activity" list in README.md from the public repos pushed to most recently."""

import json
import os
import re
import urllib.request
from datetime import datetime

USER = "ZANYANBU"
COUNT = 5
START, END = "<!-- recent-activity:start -->", "<!-- recent-activity:end -->"

request = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&per_page=30",
    headers={"Accept": "application/vnd.github+json",
             **({"Authorization": f"Bearer {os.environ['GH_TOKEN']}"} if os.environ.get("GH_TOKEN") else {})})
repos = json.load(urllib.request.urlopen(request))

lines = []
for repo in repos:
    if repo["fork"] or repo["archived"] or repo["name"] == USER:
        continue
    pushed = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")
    about = (repo["description"] or "").strip()
    lines.append(f"- **[{repo['name']}]({repo['html_url']})** — {about}  <sub>{pushed.day} {pushed:%b %Y}</sub>")
    if len(lines) == COUNT:
        break

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
block = START + "\n" + "\n".join(lines) + "\n" + END
updated, found = re.subn(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
if not found:
    raise SystemExit("README.md has no recent-activity markers")
if updated != readme:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)
    print("README.md updated")
else:
    print("no change")

"""Draw the neofetch-style profile card (dark and light SVG) for the README.

The ASCII portrait comes from .github/profile/ascii.txt (see ascii_portrait.py).
GitHub numbers are read live with the GitHub GraphQL API when GH_TOKEN is set.
    python3 .github/scripts/profile_card.py
"""
import datetime as dt
import html
import json
import os
import urllib.request

USER = "ZANYANBU"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "profile")
START = dt.date(2024, 8, 1)  # started building at SRM
WIDTH = 60                   # characters in the info column

def gql(query):
    token = os.environ.get("GH_TOKEN")
    if not token:
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]

def stats():
    years = range(2024, dt.date.today().year + 1)
    parts = " ".join(
        f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z", to:"{y}-12-31T23:59:59Z")'
        "{ totalCommitContributions restrictedContributionsCount }"
        for y in years
    )
    d = gql(
        f'{{ user(login:"{USER}") {{ followers {{ totalCount }} '
        "repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100){ totalCount nodes { stargazerCount } } "
        "repositoriesContributedTo(contributionTypes:[COMMIT, PULL_REQUEST], first:1){ totalCount } "
        f"{parts} }} }}"
    )
    if not d:
        return None
    u = d["user"]
    contrib = sum(u[f"y{y}"]["totalCommitContributions"] + u[f"y{y}"]["restrictedContributionsCount"] for y in years)
    return {
        "repos": u["repositories"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "contrib": contrib,
    }

def uptime(today):
    months = (today.year - START.year) * 12 + today.month - START.month
    days = (today - START.replace(year=today.year, month=today.month)).days if today.day >= START.day else today.day
    y, m = divmod(months, 12)
    return f"{y} years, {m} months, {days} days"

def rows(s, today):
    st = s or {"repos": "-", "contributed": "-", "stars": "-", "followers": "-", "contrib": "-"}
    fmt = lambda v: f"{v:,}" if isinstance(v, int) else v
    return [
        ("title", "anbu@zanyanbu"),
        ("kv", "OS", "macOS, iOS, Windows 11 (home server)"),
        ("kv", "Uptime", uptime(today)),
        ("kv", "Host", "SRM Institute of Science and Technology"),
        ("kv", "Kernel", "Product Engineer @ Eesa AI"),
        ("kv", "IDE", "VS Code, Xcode, Claude Code"),
        ("gap",),
        ("kv", "Languages.Programming", "Python, Dart, Swift, TypeScript"),
        ("kv", "Languages.Computer", "HTML, CSS, SQL, JSON, YAML"),
        ("kv", "Languages.Real", "Tamil, English"),
        ("gap",),
        ("kv", "Hobbies.Software", "local AI, macOS internals"),
        ("kv", "Hobbies.Hardware", "junkyard PCs, motorcycles"),
        ("gap",),
        ("head", "Contact"),
        ("kv", "Email", "zanyanbuchelvan@gmail.com"),
        ("kv", "LinkedIn", "anbuchelvan-v-aa5b11260"),
        ("kv", "Website", "zanyanbu.github.io/portfolio"),
        ("gap",),
        ("head", "GitHub Stats"),
        ("kv2", "Repos", f"{fmt(st['repos'])} {{Contributed: {fmt(st['contributed'])}}}", "Stars", fmt(st["stars"])),
        ("kv2", "Contributions", fmt(st["contrib"]), "Followers", fmt(st["followers"])),
    ]

def esc(t):
    return html.escape(t, quote=False)

def leader(key, value, width):
    dots = width - len(key) - len(value) - 4
    return f" {'.' * max(dots, 1)} "

def svg(theme, art, info):
    c = {
        "dark": dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", val="#a5d6ff", dim="#616e7f", art="#c9d1d9", head="#a5d6ff"),
        "light": dict(bg="#f6f8fa", fg="#24292f", key="#953800", val="#0a3069", dim="#c2cfde", art="#24292f", head="#0a3069"),
    }[theme]
    fs, lh = 14, 18.5
    art_fs = 11.0
    art_lh = 12.6
    x2 = 455
    h = max(len(info) * lh, len(art) * art_lh) + 60
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="985" height="{h:.0f}" viewBox="0 0 985 {h:.0f}" '
        f'font-family="ConsolasFallback, Consolas, \'JetBrains Mono\', monospace">',
        f'<rect width="985" height="{h:.0f}" rx="15" fill="{c["bg"]}"/>',
        f'<text x="20" y="30" fill="{c["art"]}" font-size="{art_fs:.2f}px" xml:space="preserve">',
    ]
    for i, line in enumerate(art):
        out.append(f'<tspan x="20" y="{30 + i * art_lh:.1f}">{esc(line)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{x2}" y="30" fill="{c["fg"]}" font-size="{fs}px" xml:space="preserve">')
    for i, r in enumerate(info):
        y = 30 + i * lh
        if r[0] == "title":
            out.append(f'<tspan x="{x2}" y="{y:.1f}" fill="{c["key"]}" font-weight="bold">{esc(r[1])}</tspan>'
                       f'<tspan fill="{c["dim"]}"> {"-" * (WIDTH - len(r[1]) - 1)}</tspan>')
        elif r[0] == "head":
            out.append(f'<tspan x="{x2}" y="{y:.1f}" fill="{c["dim"]}">- </tspan><tspan fill="{c["head"]}" font-weight="bold">{esc(r[1])}</tspan>'
                       f'<tspan fill="{c["dim"]}"> {"-" * (WIDTH - len(r[1]) - 3)}</tspan>')
        elif r[0] == "kv":
            _, k, v = r
            out.append(f'<tspan x="{x2}" y="{y:.1f}" fill="{c["dim"]}">. </tspan><tspan fill="{c["key"]}">{esc(k)}</tspan>'
                       f'<tspan fill="{c["dim"]}">:{leader(k, v, WIDTH)}</tspan><tspan fill="{c["val"]}">{esc(v)}</tspan>')
        elif r[0] == "kv2":
            _, k1, v1, k2, v2 = r
            half = 31
            out.append(f'<tspan x="{x2}" y="{y:.1f}" fill="{c["dim"]}">. </tspan><tspan fill="{c["key"]}">{esc(k1)}</tspan>'
                       f'<tspan fill="{c["dim"]}">:{leader(k1, v1, half)}</tspan><tspan fill="{c["val"]}">{esc(v1)}</tspan>'
                       f'<tspan fill="{c["dim"]}"> | </tspan><tspan fill="{c["key"]}">{esc(k2)}</tspan>'
                       f'<tspan fill="{c["dim"]}">:{leader(k2, v2, WIDTH - half - 3)}</tspan><tspan fill="{c["val"]}">{esc(v2)}</tspan>')
    out.append("</text></svg>")
    return "\n".join(out)

def load_stats():
    """Live numbers, but never let a count go down: the Actions token cannot see
    private contributions, so the last number seen with a full token is kept."""
    path = os.path.join(OUT, "stats.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    new = stats() or {}
    merged = {k: max(v, old.get(k, 0)) if k == "contrib" else v for k, v in new.items()}
    for k, v in old.items():
        merged.setdefault(k, v)
    if merged:
        with open(path, "w") as f:
            json.dump(merged, f, indent=2, sort_keys=True)
    return merged or None

def main():
    read = lambda n: open(os.path.join(OUT, n)).read().rstrip("\n").split("\n")
    info = rows(load_stats(), dt.date.today())
    for theme, art in (("dark", read("ascii.txt")), ("light", read("ascii-light.txt"))):
        with open(os.path.join(OUT, f"card-{theme}.svg"), "w") as f:
            f.write(svg(theme, art, info))

if __name__ == "__main__":
    main()

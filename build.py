#!/usr/bin/env python3
"""Buduje statyczną stronę ivoadventures.pl z site.json + posts/*.md.

Użycie:
  python3 build.py            -> public/   (do wrzucenia na serwer / GitHub Pages)
  python3 build.py --preview  -> preview/  (linki z index.html, do podglądu offline)
"""
import json, re, sys, shutil, html
from pathlib import Path
from datetime import date
import markdown, yaml

ROOT = Path(__file__).parent
PREVIEW = "--preview" in sys.argv
OUT = ROOT / ("preview" if PREVIEW else "public")
S = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
MONTHS = ["stycznia","lutego","marca","kwietnia","maja","czerwca","lipca",
          "sierpnia","września","października","listopada","grudnia"]

def esc(s): return html.escape(s, quote=True)
def pl_date(d): return f"{d.day} {MONTHS[d.month-1]} {d.year}"

def link(rel, path):
    """path np. '' (główna), 'aktualnosci/', 'aktualnosci/slug/'. rel = '../' * głębokość."""
    if PREVIEW:
        return rel + path + "index.html"
    return rel + path if (rel + path) else "./"

def parse_post(p):
    raw = p.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw.replace("\r\n", "\n"), re.S)
    meta = yaml.safe_load(m.group(1)) or {}
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", p.stem)
    d = meta["date"]
    d = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
    draft = meta.get("draft", False)
    return {
        "slug": slug,
        "title": str(meta["title"]),
        "date": d,
        "description": str(meta.get("description") or ""),
        "category": str(meta.get("category") or "Aktualności"),
        "image": str(meta.get("image") or "").lstrip("/"),
        "html": markdown.markdown(m.group(2), extensions=["extra"]),
        "draft": draft is True or str(draft).lower() in ("true", "tak", "yes"),
    }

posts = sorted((parse_post(p) for p in (ROOT / "posts").glob("*.md")),
               key=lambda x: x["date"], reverse=True)
posts = [p for p in posts if not p["draft"]]

PERSON_LD = {
    "@context": "https://schema.org", "@type": "Person",
    "name": S["name"], "alternateName": [S["brand"], "Ivo Adventures", "Ivo"],
    "url": S["url"] + "/", "description": S["description"],
    "jobTitle": "Twórczyni internetowa, ekspertka DIY",
    "email": "mailto:" + S["email"],
    "sameAs": [s["url"] for s in S["socials"]],
}

def avatar(rel):
    if S["photo"]:
        return f'<span class="ring"><img class="avatar" src="{rel}{esc(S["photo"])}" alt="{esc(S["name"])} – {esc(S["brand"])}" width="140" height="140"></span>'
    return '<div class="avatar mono" aria-hidden="true">Ivo</div>'

def page(rel, path, title, desc, body, ld=None, og_type="website", image=""):
    canonical = S["url"] + "/" + path
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    og_img = f'<meta property="og:image" content="{S["url"]}/{esc(image or S["photo"])}">' if (image or S["photo"]) else ""
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="{esc(S['brand'])} – {esc(S['name'])}">
{og_img}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}style.css">
{lds}
</head>
<body>
<header class="top"><a class="logo" href="{link(rel, '')}">Ivo<span>Adventures</span></a>
<nav><a href="{link(rel, 'aktualnosci/')}">Aktualności</a><a href="{link(rel, '')}#wspolpraca">Współpraca</a></nav></header>
<main>
{body}
</main>
<footer><p>© {date.today().year} {esc(S['name'])} · {esc(S['brand'])}</p>
<p><a href="mailto:{S['email']}">{S['email']}</a></p></footer>
</body>
</html>
"""

def post_card(p, rel):
    return f"""<a class="card" href="{link(rel, 'aktualnosci/' + p['slug'] + '/')}">
<span class="meta">{esc(p['category'])} · {pl_date(p['date'])}</span>
<h3>{esc(p['title'])}</h3><p>{esc(p['description'])}</p></a>"""

def write(path, content):
    f = OUT / path / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")

if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
shutil.copy(ROOT / "style.css", OUT / "style.css")
for d in ("img", "pliki"):
    if (ROOT / d).exists(): shutil.copytree(ROOT / d, OUT / d)
if not PREVIEW:
    (OUT / "CNAME").write_text(S["url"].split("//")[1] + "\n")

# --- strona główna (link in bio) ---
socials = "".join(f'<a class="btn" href="{esc(s["url"])}" rel="me noopener" target="_blank"><b>{esc(s["label"])}</b><span>{esc(s["count"])}</span></a>' for s in S["socials"])
media = "".join(f"<li>{esc(m)}</li>" for m in S["media"])
latest = "".join(post_card(p, "") for p in posts[:3])
vids = "".join(f'<a class="vid" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener"><span class="thumb"><img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="{esc(v["title"])}" loading="lazy" width="480" height="360"><i>▶</i></span><b>{esc(v["title"])}</b></a>' for v in S.get("videos", []))
home = f"""<section class="hero">
{avatar('')}
<h1>{esc(S['name'])}<small>{esc(S['brand'])}</small></h1>
<p class="tag">{esc(S['tagline'])}</p>
<p class="bio">{esc(S['bio'])}</p>
</section>
<section class="links">{socials}
<a class="btn accent" href="mailto:{S['email']}?subject=Wsp%C3%B3%C5%82praca%20z%20IvoAdventures"><b>Współpraca z marką</b><span>napisz</span></a></section>
<section><div class="head"><h2>Aktualności</h2><a href="{link('', 'aktualnosci/')}">wszystkie →</a></div>
<div class="cards">{latest}</div></section>
<section><div class="head"><h2>Popularne filmy</h2><a href="https://youtube.com/@ivoadventures" target="_blank" rel="noopener">YouTube →</a></div>
<div class="vids">{vids}</div></section>
<section class="media"><h2>Ivo w mediach</h2><ul>{media}</ul></section>
<section id="wspolpraca" class="contact"><h2>Współpraca</h2>
<p>Jesteś marką i chcesz współpracować z Ivo? Napisz – odpowiemy i wyślemy media kit.</p>
<p><a class="btn accent" href="mailto:{S['email']}"><b>{S['email']}</b></a></p>
<p class="small">Kontakt: Kacper Kuziora, manager</p></section>"""
write("", page("", "", f"{S['name']} – {S['brand']} | {S['tagline']}", S["description"], home, [PERSON_LD]))

# --- lista wpisów ---
all_cards = "".join(post_card(p, "../") for p in posts)
write("aktualnosci", page("../", "aktualnosci/", f"Aktualności – {S['name']} ({S['brand']})",
      f"Nowe DIY, występy w telewizji i radiu, współprace. Aktualności z życia {S['name']} – {S['brand']}.",
      f'<section><h1 class="pt">Aktualności</h1><div class="cards">{all_cards}</div></section>'))

# --- pojedyncze wpisy ---
for p in posts:
    rel = "../../"
    path = f"aktualnosci/{p['slug']}/"
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
          "description": p["description"], "datePublished": p["date"].isoformat(),
          "inLanguage": "pl", "mainEntityOfPage": S["url"] + "/" + path,
          "author": {"@type": "Person", "name": S["name"], "url": S["url"] + "/"},
          "about": {"@type": "Person", "name": S["name"], "alternateName": S["brand"]}}
    img = f'<img class="cover" src="{rel}{esc(p["image"])}" alt="{esc(p["title"])}">' if p["image"] else ""
    body = f"""<article class="post">
<a class="back" href="{link(rel, 'aktualnosci/')}">← Aktualności</a>
<span class="meta">{esc(p['category'])} · <time datetime="{p['date'].isoformat()}">{pl_date(p['date'])}</time></span>
<h1>{esc(p['title'])}</h1>{img}
<div class="prose">{p['html']}</div>
<aside class="author">{avatar(rel)}<div><b>{esc(S['name'])} · {esc(S['brand'])}</b><p>{esc(S['tagline'])}. <a href="{link(rel, '')}">Wszystkie linki →</a></p></div></aside>
</article>"""
    write(path, page(rel, path, f"{p['title']} | {S['brand']}", p["description"], body, [ld], "article", p["image"]))


# --- SEO: sitemap + robots ---
urls = [("", date.today()), ("aktualnosci/", posts[0]["date"] if posts else date.today())]
urls += [(f"aktualnosci/{p['slug']}/", p["date"]) for p in posts]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"<url><loc>{S['url']}/{u}</loc><lastmod>{d.isoformat()}</lastmod></url>\n" for u, d in urls) + "</urlset>\n", encoding="utf-8")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {S['url']}/sitemap.xml\n")
print(f"OK: {len(posts)} wpisów -> {OUT}")

#!/usr/bin/env python3
"""Buduje statyczną stronę ivoadventures.pl z site.json + posts/*.md + pages/*.md.

Użycie:
  python3 build.py                     -> public/   (to idzie na GitHub Pages)
  python3 build.py --preview           -> preview/  (linki z index.html, do podglądu offline)
  python3 build.py --preview --drafts  -> preview/  razem ze szkicami (oznaczone „SZKIC”)
"""
import json, re, sys, shutil, html, unicodedata
from pathlib import Path
from datetime import date
import markdown, yaml

ROOT = Path(__file__).parent
PREVIEW = "--preview" in sys.argv
DRAFTS = "--drafts" in sys.argv
OUT = ROOT / ("preview" if PREVIEW else "public")
S = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
MONTHS = ["stycznia","lutego","marca","kwietnia","maja","czerwca","lipca",
          "sierpnia","września","października","listopada","grudnia"]

def esc(s): return html.escape(str(s), quote=True)
def pl_date(d): return f"{d.day} {MONTHS[d.month-1]} {d.year}"
def slugify(s):
    s = s.lower().replace("ł", "l")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def link(rel, path):
    """path np. '' (główna), 'aktualnosci/', 'aktualnosci/slug/'. rel = '../' * głębokość."""
    if PREVIEW:
        return rel + path + "index.html"
    return rel + path if (rel + path) else "./"

def read_md(p):
    raw = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)

def parse_post(p):
    meta, body = read_md(p)
    d = meta["date"]
    d = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
    draft = meta.get("draft", False)
    cat = str(meta.get("category") or "Aktualności")
    return {
        "slug": re.sub(r"^\d{4}-\d{2}-\d{2}-", "", p.stem),
        "title": str(meta["title"]), "date": d,
        "description": str(meta.get("description") or ""),
        "category": cat, "cat_slug": slugify(cat),
        "image": str(meta.get("image") or "").lstrip("/"),
        "youtube": str(meta.get("youtube") or "").strip(),
        "html": markdown.markdown(body, extensions=["extra"]),
        "draft": draft is True or str(draft).lower() in ("true", "tak", "yes"),
        "pinned": meta.get("pinned") is True,
    }

posts = sorted((parse_post(p) for p in (ROOT / "posts").glob("*.md")),
               key=lambda x: (x["date"], x["slug"]), reverse=True)
posts.sort(key=lambda x: not x["pinned"])  # przypięte na górze, reszta wg daty
posts = [p for p in posts if DRAFTS or not p["draft"]]
CATS = []
for c in S.get("categories", []) + [p["category"] for p in posts]:
    if c not in CATS and any(p["category"] == c for p in posts): CATS.append(c)

PERSON_LD = {
    "@context": "https://schema.org", "@type": "Person",
    "name": S["name"], "alternateName": [S["brand"], "Ivo Adventures", "Ivo"],
    "url": S["url"] + "/", "description": S["description"],
    "jobTitle": "Twórczyni internetowa, ekspertka DIY",
    "email": "mailto:" + S["email"],
    "sameAs": [s["url"] for s in S["socials"]],
}
if S.get("photo"): PERSON_LD["image"] = S["url"] + "/" + S["photo"]

def avatar(rel):
    if S["photo"]:
        return f'<span class="ring"><img class="avatar" src="{rel}{esc(S["photo"])}" alt="{esc(S["name"])} – {esc(S["brand"])}" width="140" height="140"></span>'
    return '<div class="avatar mono" aria-hidden="true">Ivo</div>'

def page(rel, path, title, desc, body, ld=None, og_type="website", image=""):
    canonical = S["url"] + "/" + path
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    img = image or S["photo"]
    og_img = ""
    if img:
        og_img = f'<meta property="og:image" content="{img if img.startswith("http") else S["url"] + "/" + esc(img)}">'
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
<nav><a href="{link(rel, 'aktualnosci/')}">Wpisy</a><a href="{link(rel, 'o-ivo/')}">O Ivo</a><a href="{link(rel, '')}#wspolpraca">Kontakt</a></nav></header>
<main>
{body}
</main>
<footer><p>© {date.today().year} {esc(S['name'])} · {esc(S['brand'])}</p>
<p><a href="{link(rel, 'o-ivo/')}">O Ivo</a> · <a href="{link(rel, 'aktualnosci/')}">Wszystkie wpisy</a> · <a href="mailto:{S['email']}">{S['email']}</a></p></footer>
</body>
</html>
"""

def thumb_of(p, rel):
    if p["image"]: return rel + p["image"]
    if p["youtube"]: return f"https://i.ytimg.com/vi/{p['youtube']}/hqdefault.jpg"
    return ""

def post_card(p, rel):
    t = thumb_of(p, rel)
    timg = f'<img src="{esc(t)}" alt="" loading="lazy">' if t else ""
    badge = '<em class="draft">SZKIC</em> ' if p["draft"] else ""
    return f"""<a class="card{' has-img' if t else ''}" href="{link(rel, 'aktualnosci/' + p['slug'] + '/')}">{timg}<span class="ctext">
<span class="meta">{esc(p['category'])} · {pl_date(p['date'])}</span>
<h3>{badge}{esc(p['title'])}</h3><p>{esc(p['description'])}</p></span></a>"""

def cat_pills(rel, active=""):
    pills = [f'<a class="pill{" on" if not active else ""}" href="{link(rel, "aktualnosci/")}">Wszystkie</a>']
    pills += [f'<a class="pill{" on" if c == active else ""}" href="{link(rel, "kategoria/" + slugify(c) + "/")}">{esc(c)}</a>' for c in CATS]
    return '<nav class="pills catnav">' + "".join(pills) + "</nav>"

def yt_embed(vid, title):
    return (f'<div class="yt"><iframe src="https://www.youtube-nocookie.com/embed/{esc(vid)}" title="{esc(title)}" '
            f'loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>')

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
latest = "".join(post_card(p, "") for p in posts[:4])
vids = "".join(f'<a class="vid" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener"><span class="thumb"><img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="{esc(v["title"])}" loading="lazy" width="480" height="360"><i>▶</i></span><b>{esc(v["title"])}</b></a>' for v in S.get("videos", []))
home = f"""<section class="hero">
{avatar('')}
<h1>{esc(S['name'])}<small>{esc(S['brand'])}</small></h1>
<p class="tag">{esc(S['tagline'])}</p>
<p class="bio">{esc(S['bio'])} <a class="more" href="{link('', 'o-ivo/')}">Więcej o Ivo →</a></p>
</section>
<section class="links">{socials}
<a class="btn accent" href="mailto:{S['email']}?subject=Wsp%C3%B3%C5%82praca%20z%20IvoAdventures"><b>Współpraca z marką</b><span>napisz</span></a></section>
<section><div class="head"><h2>Najnowsze wpisy</h2><a href="{link('', 'aktualnosci/')}">wszystkie →</a></div>
{cat_pills('')}
<div class="cards">{latest}</div></section>
<section><div class="head"><h2>Popularne filmy</h2><a href="https://youtube.com/@ivoadventures" target="_blank" rel="noopener">YouTube →</a></div>
<div class="vids">{vids}</div></section>
<section class="media"><h2>Ivo w mediach</h2><ul>{media}</ul></section>
<section id="wspolpraca" class="contact"><h2>Współpraca</h2>
<p>Jesteś marką i chcesz współpracować z Ivo? Napisz – odpowiemy i wyślemy media kit.</p>
<p><a class="btn accent" href="mailto:{S['email']}"><b>{S['email']}</b></a></p>
<p class="small">Kontakt: Kacper Kuziora, manager</p></section>"""
write("", page("", "", f"{S['name']} – {S['brand']} | {S['tagline']}", S["description"], home, [PERSON_LD]))

# --- lista wpisów + kategorie ---
all_cards = "".join(post_card(p, "../") for p in posts)
write("aktualnosci", page("../", "aktualnosci/", f"Wpisy – {S['name']} ({S['brand']})",
      f"Poradniki DIY, występy w telewizji, starocie i remont domu. Wszystkie wpisy {S['name']} – {S['brand']}.",
      f'<section><h1 class="pt">Wpisy</h1>{cat_pills("../")}<div class="cards">{all_cards}</div></section>'))
CAT_DESC = S.get("category_descriptions", {})
for c in CATS:
    rel = "../../"
    cs = slugify(c)
    cards = "".join(post_card(p, rel) for p in posts if p["category"] == c)
    intro = CAT_DESC.get(c, "")
    write(f"kategoria/{cs}", page(rel, f"kategoria/{cs}/", f"{c} – {S['name']} ({S['brand']})",
          intro or f"{c}: wpisy {S['name']} ({S['brand']}).",
          f'<section><h1 class="pt">{esc(c)}</h1>{f"<p class=bio-l>{esc(intro)}</p>" if intro else ""}{cat_pills(rel, c)}<div class="cards">{cards}</div></section>'))

# --- pojedyncze wpisy ---
def related(p):
    same = [q for q in posts if q is not p and q["category"] == p["category"]]
    other = [q for q in posts if q is not p and q not in same]
    return (same + other)[:3]

for p in posts:
    rel = "../../"
    path = f"aktualnosci/{p['slug']}/"
    lds = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
            "description": p["description"], "datePublished": p["date"].isoformat(),
            "inLanguage": "pl", "mainEntityOfPage": S["url"] + "/" + path,
            "image": (thumb_of(p, S["url"] + "/") or S["url"] + "/" + S["photo"]),
            "author": {"@type": "Person", "name": S["name"], "url": S["url"] + "/o-ivo/"},
            "about": {"@type": "Person", "name": S["name"], "alternateName": S["brand"]}}]
    if p["youtube"]:
        lds.append({"@context": "https://schema.org", "@type": "VideoObject", "name": p["title"],
                    "description": p["description"], "uploadDate": p["date"].isoformat(),
                    "thumbnailUrl": f"https://i.ytimg.com/vi/{p['youtube']}/hqdefault.jpg",
                    "embedUrl": f"https://www.youtube.com/embed/{p['youtube']}",
                    "contentUrl": f"https://www.youtube.com/watch?v={p['youtube']}"})
    img = f'<img class="cover" src="{rel}{esc(p["image"])}" alt="{esc(p["title"])}">' if p["image"] else ""
    video = yt_embed(p["youtube"], p["title"]) if p["youtube"] else ""
    rel_cards = "".join(post_card(q, rel) for q in related(p))
    badge = '<em class="draft">SZKIC – niewidoczny na stronie</em>' if p["draft"] else ""
    body = f"""<article class="post">
<a class="back" href="{link(rel, 'kategoria/' + p['cat_slug'] + '/')}">← {esc(p['category'])}</a>
{badge}<span class="meta">{esc(p['category'])} · <time datetime="{p['date'].isoformat()}">{pl_date(p['date'])}</time></span>
<h1>{esc(p['title'])}</h1>{img}{video}
<div class="prose">{p['html']}</div>
<aside class="author">{avatar(rel)}<div><b>{esc(S['name'])} · {esc(S['brand'])}</b><p>{esc(S['tagline'])}. <a href="{link(rel, 'o-ivo/')}">Więcej o Ivo →</a></p></div></aside>
</article>
<section><h2>Zobacz też</h2><div class="cards">{rel_cards}</div></section>"""
    write(path, page(rel, path, f"{p['title']} | {S['brand']}", p["description"], body, lds, "article", thumb_of(p, "")))

# --- strony stałe (pages/*.md), np. O Ivo ---
static_pages = []
for f in sorted((ROOT / "pages").glob("*.md")) if (ROOT / "pages").exists() else []:
    meta, body = read_md(f)
    slug = f.stem
    rel = "../"
    ld = [dict(PERSON_LD, **{"description": meta.get("description", S["description"])})] if slug == "o-ivo" else []
    content = f"""<article class="post page-{slug}">{avatar(rel) if slug == 'o-ivo' else ''}
<h1>{esc(meta['title'])}</h1>
<div class="prose">{markdown.markdown(body, extensions=['extra'])}</div></article>"""
    write(slug, page(rel, f"{slug}/", f"{meta['title']} | {S['name']} – {S['brand']}", meta.get("description", ""), content, ld, "profile" if slug == "o-ivo" else "website"))
    static_pages.append(slug)

# --- SEO: sitemap + robots ---
if not DRAFTS:
    urls = [("", date.today()), ("aktualnosci/", posts[0]["date"] if posts else date.today())]
    urls += [(f"{s}/", date.today()) for s in static_pages]
    urls += [(f"kategoria/{slugify(c)}/", date.today()) for c in CATS]
    urls += [(f"aktualnosci/{p['slug']}/", p["date"]) for p in posts]
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"<url><loc>{S['url']}/{u}</loc><lastmod>{d.isoformat()}</lastmod></url>\n" for u, d in urls) + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {S['url']}/sitemap.xml\n")
print(f"OK: {len(posts)} wpisów ({sum(p['draft'] for p in posts)} szkiców), kategorie: {', '.join(CATS)} -> {OUT}")

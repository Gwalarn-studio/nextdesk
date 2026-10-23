"""Build the static site: wraps content/<lang>/<slug>.html fragments in the shared layout.

Each fragment starts with a JSON header between <!--meta and -->:
  {"title", "description", "rubric", "dek", "pair" (slug in the other language),
   "date" (YYYY-MM-DD), "kind": "article" | "tool", "card": short teaser}
"""
import json, pathlib, re, html

ROOT = pathlib.Path(__file__).parent
BASE_URL = "https://gwalarn-studio.github.io/nextdesk/"
SERVICES = "https://gwalarn-studio.github.io/Plume-and-go/"

T = {
 "en": {"home": "Home", "tools": "Free tools", "services": "Get your CV done", "other": "FR", "other_lang": "fr",
        "tag": "Careers, remote work and AI, explained simply.",
        "legal": "Legal notice", "privacy": "Privacy", "terms": "Terms",
        "promo_h": "Short on time?", "promo_p": "A human writer rewrites your CV or LinkedIn profile in English or French. Delivered within 24 hours.",
        "promo_b": "See the services", "read": "Read", "updated": "Updated",
        "disc": "Some links on this site are affiliate links: if you buy through them we may earn a commission, at no extra cost to you. We only recommend tools we would use.",
        "rubrics": {"cv": "CV & applications", "remote": "Remote work", "ai": "AI at work", "tools": "Free tools"}},
 "fr": {"home": "Accueil", "tools": "Outils gratuits", "services": "Faire refaire mon CV", "other": "EN", "other_lang": "en",
        "tag": "Carrière, télétravail et IA, expliqués simplement.",
        "legal": "Mentions légales", "privacy": "Confidentialité", "terms": "CGV",
        "promo_h": "Pas le temps ?", "promo_p": "Un rédacteur réécrit votre CV ou votre profil LinkedIn en français ou en anglais. Livré en 24 heures.",
        "promo_b": "Voir les services", "read": "Lire", "updated": "Mis à jour le",
        "disc": "Certains liens de ce site sont affiliés : si vous achetez par leur biais, nous pouvons toucher une commission, sans surcoût pour vous. Nous ne recommandons que des outils que nous utiliserions.",
        "rubrics": {"cv": "CV et candidature", "remote": "Travail à distance", "ai": "IA au travail", "tools": "Outils gratuits"}},
}
LEGAL = {"en": ("legal-notice.html", "privacy.html", "terms.html"),
         "fr": ("legal-notice.html?lang=fr", "privacy.html?lang=fr", "terms.html?lang=fr")}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800'
         '&family=Figtree:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')

def fmt_date(d, lang):
    y, m, dd = d.split("-")
    if lang == "fr":
        mois = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()
        return f"{int(dd)} {mois[int(m)-1]} {y}"
    months = "January February March April May June July August September October November December".split()
    return f"{months[int(m)-1]} {int(dd)}, {y}"

def head(lang, title, desc, path, alt_path, extra=""):
    canon = BASE_URL + path
    alt = BASE_URL + alt_path if alt_path is not None else None
    links = f'<link rel="canonical" href="{canon}">'
    if alt is not None:
        other = T[lang]["other_lang"]
        links += (f'<link rel="alternate" hreflang="{lang}" href="{canon}">'
                  f'<link rel="alternate" hreflang="{other}" href="{alt}">')
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canon}">
{links}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230f4b45'/%3E%3Ctext x='16' y='22' font-size='17' font-family='sans-serif' font-weight='800' text-anchor='middle' fill='%23ffe45c'%3EN%3C/text%3E%3C/svg%3E">
{FONTS}
<link rel="stylesheet" href="{rel(path)}assets/style.css">{extra}
</head><body>"""

def rel(path):
    depth = path.count("/")
    return "../" * depth

def nav(lang, path, alt_path):
    t = T[lang]; r = rel(path)
    home = f"{r}index.html" if lang == "en" else f"{r}fr/index.html"
    tools = f"{r}{lang}/" + ("remote-job-quiz.html" if lang == "en" else "quiz-metier-teletravail.html")
    other = f"{r}{alt_path}" if alt_path is not None else (f"{r}fr/index.html" if lang == "en" else f"{r}index.html")
    return f"""<header class="band"><div class="wrap nav">
<a class="logo" href="{home}">Next<span>Desk</span></a>
<nav class="menu" aria-label="Menu"><a class="hide-sm" href="{tools}">{t['tools']}</a>
<a class="lang" href="{other}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other']}</a>
<a class="cta" href="{SERVICES}?lang={lang}">{t['services']}</a></nav></div>"""

def footer(lang, path):
    t = T[lang]; l = LEGAL[lang]
    return f"""<footer><div class="wrap row"><span>NextDesk · {t['tag']}</span>
<nav><a href="{SERVICES}{l[0]}">{t['legal']}</a><a href="{SERVICES}{l[1]}">{t['privacy']}</a><a href="{SERVICES}{l[2]}">{t['terms']}</a></nav>
</div></footer><script src="{rel(path)}assets/site.js" defer></script></body></html>"""

def promo(lang):
    t = T[lang]
    return f"""<div class="box promo"><h3>{t['promo_h']}</h3><p>{t['promo_p']}</p>
<a class="btn btn-mark" href="{SERVICES}?lang={lang}">{t['promo_b']}</a></div>"""

def load(lang):
    out = []
    for f in sorted((ROOT / "content" / lang).glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->", raw, re.S)
        meta = json.loads(m.group(1)); meta["slug"] = f.stem; meta["body"] = raw[m.end():]
        out.append(meta)
    return out

def build_article(lang, a, related):
    t = T[lang]
    path = f"{lang}/{a['slug']}.html"
    other = t["other_lang"]
    alt_path = f"{other}/{a['pair']}.html" if a.get("pair") else None
    home = rel(path) + ("index.html" if lang == "en" else "fr/index.html")
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
                     "description": a["description"], "inLanguage": lang, "dateModified": a["date"],
                     "publisher": {"@type": "Organization", "name": "NextDesk"}}, ensure_ascii=False)
    rel_list = "".join(f'<li><a href="{r["slug"]}.html">{html.escape(r["title"])}</a></li>' for r in related)
    page = head(lang, a["title"] + " | NextDesk", a["description"], path, alt_path,
                f'<script type="application/ld+json">{ld}</script>')
    page += nav(lang, path, alt_path)
    page += f"""<div class="wrap article-head">
<div class="crumbs"><a href="{home}">{t['home']}</a> / {t['rubrics'][a['rubric']]}</div>
<h1>{a['h1'] if a.get('h1') else html.escape(a['title'])}</h1>
<p class="dek">{a['dek']}</p>
<div class="byline">{t['updated']} {fmt_date(a['date'], lang)}</div></div></header>
<main class="wrap layout"><article class="prose">{a['body']}
<p class="disclosure">{t['disc']}</p></article>
<aside class="side">{promo(lang)}<div class="box"><h3>{'Read next' if lang=='en' else 'À lire aussi'}</h3><ul>{rel_list}</ul></div></aside></main>"""
    page += footer(lang, path)
    (ROOT / "docs" / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / path).write_text(page, encoding="utf-8")
    return path

def build_home(lang, items):
    t = T[lang]
    path = "index.html" if lang == "en" else "fr/index.html"
    alt = "fr/index.html" if lang == "en" else "index.html"
    if lang == "en":
        title = "NextDesk: land a remote job, write a CV that gets read, use AI at work"
        desc = "Free guides, CV examples and tools for job seekers and remote workers, in English and French."
        h1 = "Your next job, <em>from anywhere</em>."
        lead = "Practical guides, CV examples you can copy and free tools to land a remote job and work smarter with AI."
        latest, rub_h = "Latest guides", "What you will find here"
        rub_d = {"cv": "CV examples, cover letters, LinkedIn and interviews.", "remote": "Companies hiring, job boards, salaries, visas.",
                 "ai": "Prompts and tools that save you hours.", "tools": "Quizzes, generators and checklists."}
        strip = ("Want a CV that gets interviews?", "Plume & Go rewrites your CV, cover letter or LinkedIn profile. Human-reviewed, delivered within 24 hours.", "See prices")
    else:
        title = "NextDesk : trouver un emploi en télétravail, un CV qui accroche, l'IA au travail"
        desc = "Guides gratuits, exemples de CV et outils pour chercher un emploi et travailler à distance, en français et en anglais."
        h1 = "Votre prochain job, <em>de n'importe où</em>."
        lead = "Des guides concrets, des exemples de CV à copier et des outils gratuits pour décrocher un poste en télétravail et gagner du temps avec l'IA."
        latest, rub_h = "Derniers guides", "Ce que vous trouverez ici"
        rub_d = {"cv": "Exemples de CV, lettres, LinkedIn et entretiens.", "remote": "Entreprises qui recrutent, sites d'emploi, salaires, visas.",
                 "ai": "Prompts et outils qui font gagner des heures.", "tools": "Quiz, générateurs et checklists."}
        strip = ("Un CV qui décroche des entretiens ?", "Plume & Go réécrit votre CV, votre lettre ou votre profil LinkedIn. Relu par un humain, livré en 24 heures.", "Voir les tarifs")
    page = head(lang, title, desc, path, alt) + nav(lang, path, alt)
    page += f"""<div class="wrap hero"><span class="eyebrow">{t['tag']}</span><h1>{h1}</h1><p>{lead}</p></div></header><main>"""
    cards = ""
    for i, a in enumerate(sorted(items, key=lambda x: (x.get("kind") != "tool", x["date"]), reverse=False)):
        cls = "card feature" if a.get("kind") == "tool" else "card"
        cards += f"""<a class="{cls}" href="{lang}/{a['slug']}.html"><span class="tag">{t['rubrics'][a['rubric']]}</span>
<h3>{html.escape(a['title'])}</h3><p>{a['card']}</p></a>"""
    if lang == "fr":
        cards = cards.replace('href="fr/', 'href="')
    page += f"""<section class="wrap"><div class="sec-head"><h2>{latest}</h2></div><div class="grid">{cards}</div></section>
<section class="wrap" style="padding-top:0"><div class="strip"><div><h2>{strip[0]}</h2><p>{strip[1]}</p></div>
<a class="btn btn-mark" href="{SERVICES}?lang={lang}">{strip[2]}</a></div></section>
<section class="wrap" style="padding-top:0"><div class="sec-head"><h2>{rub_h}</h2></div><div class="rubrics">
{''.join(f'<div class="rubric"><b>{t["rubrics"][k]}</b><span>{v}</span></div>' for k, v in rub_d.items())}</div></section></main>"""
    page += footer(lang, path)
    (ROOT / "docs" / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / path).write_text(page, encoding="utf-8")
    return path

def main():
    import shutil
    docs = ROOT / "docs"
    if docs.exists(): shutil.rmtree(docs)
    docs.mkdir()
    shutil.copytree(ROOT / "assets", docs / "assets")
    urls = []
    for lang in ("en", "fr"):
        items = load(lang)
        for a in items:
            related = [r for r in items if r["slug"] != a["slug"]][:4]
            urls.append((build_article(lang, a, related), a["date"]))
        urls.append((build_home(lang, items), max(a["date"] for a in items)))
    sm = "".join(f"<url><loc>{BASE_URL}{'' if p == 'index.html' else p}</loc><lastmod>{d}</lastmod></url>" for p, d in urls)
    (docs / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>', encoding="utf-8")
    (docs / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")
    (docs / ".nojekyll").write_text("")
    print(len(urls), "pages")

if __name__ == "__main__":
    main()

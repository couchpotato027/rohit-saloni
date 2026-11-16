#!/usr/bin/env python3
"""Generate the themed invitation variants from the full-card page.

Reads  index.html + style.css (the full card, the single source of truth)
Writes sangeet/, sangeet-wedding/ and dec-1-2/ (each: index.html + style.css)

Photos, family names and the footer stay identical; only the invitation
(events, hero copy, venue, theme colours) changes per variant.
Re-run after editing the full card:  python3 tools/build_variants.py
"""
import re
import pathlib

SITE = pathlib.Path(__file__).resolve().parent.parent
BASE_URL = "https://couchpotato027.github.io/rohit-saloni"
SRC_HTML = (SITE / "index.html").read_text(encoding="utf-8")
SRC_CSS = (SITE / "style.css").read_text(encoding="utf-8")


# ---------------------------------------------------------------- helpers
def swap(html, old, new):
    """Replace a literal string; fail loudly if the source page changed shape."""
    if old not in html:
        raise ValueError(f"not found in index.html: {old[:70]!r}")
    return html.replace(old, new)


def swap_re(html, pattern, new, flags=re.S):
    out, n = re.subn(pattern, lambda _m: new, html, count=1, flags=flags)
    if n != 1:
        raise ValueError(f"pattern not found in index.html: {pattern[:70]!r}")
    return out


def swap_block(html, name, new):
    """Replace one <!-- ==== NAME ==== --> section up to the next marker or </main>."""
    pattern = rf"<!-- ============ {name} ============ -->.*?(?=<!-- ============ |</main>)"
    return swap_re(html, pattern, f"<!-- ============ {name} ============ -->\n{new}\n\n")


# ---------------------------------------------------------------- events
ACTIONS = """<div class="actions">
            <button class="chip" data-card="{card}" type="button">View card</button>
            <button class="chip" data-cal type="button">Add to calendar</button>
            <a class="chip" data-dir target="_blank" rel="noopener">Directions</a>
          </div>"""

SHREE = "Shree Ram International Jodhpur"


def ev(title, start, hours, loc, q, dow, day, card, time, venue):
    return f"""      <article class="ev reveal-card" data-title="{title}" data-start="{start}" data-hours="{hours}" data-loc="{loc}" data-q="{q}">
        <div class="ev-date"><small>{dow}</small><b>{day}</b><small>Dec</small></div>
        <div class="ev-body">
          <h3>{title}</h3>
          <p class="time">{time}</p>
          <p class="venue"><span>Venue</span> {venue}</p>
          {ACTIONS.format(card=card)}
        </div>
      </article>
"""


CARNIVAL = ev("Carnival of Love", "2026-12-01T10:15", 4, "Thar Plot, Shree Ram International, Jodhpur", SHREE, "Tue", "01", 4,
              "10:15 AM onwards · Followed by Lunch", "Thar Plot<br>Shree Ram International, Jodhpur")
TILAK = ev("Tilak", "2026-12-01T17:15", 2, "Lounge Hall, near Reception, Shri Ram International, Jodhpur", SHREE, "Tue", "01", 5,
           "5:15 PM onwards", "Lounge Hall, near Reception<br>Shri Ram International, Jodhpur")
SANGEET = ev("Sangeet", "2026-12-01T19:30", 4, "Utsav Lawn, Shree Ram International, Jodhpur", SHREE, "Tue", "01", 6,
             "7:30 PM onwards · Followed by Dinner", "Utsav Lawn<br>Shree Ram International, Jodhpur")
MAYRA = ev("Mayra", "2026-12-02T10:15", 4, "Thar Plot, Shree Ram International, Jodhpur", SHREE, "Wed", "02", 7,
           "10:15 AM onwards · Followed by Lunch", "Thar Plot<br>Shree Ram International, Jodhpur")
WEDDING = f"""      <article class="ev ev-main reveal-card" data-title="Wedding — Baraat Procession" data-start="2026-12-02T17:00" data-hours="6" data-loc="Residence “Satyam”, 59, 1st Polo, Paota, Jodhpur" data-q="59 1st Polo Paota Jodhpur">
        <div class="ev-date"><small>Wed</small><b>02</b><small>Dec</small></div>
        <div class="ev-body">
          <span class="badge">The Wedding</span>
          <h3>Wedding</h3>
          <ol class="steps">
            <li><b>5:00 PM</b><div><strong>Baraat Procession</strong><span>From the residence “Satyam”, 59, 1st Polo, Paota, Jodhpur</span></div></li>
            <li><b>6:00 PM</b><div><strong>Baraat Re-Assemble</strong><span>At Chandra Inn Hotel</span></div></li>
            <li><b>7:30 PM</b><div><strong>Reception</strong><span>Onwards, followed by Dinner · Utsav Lawn, Shree Ram International, Jodhpur</span></div></li>
          </ol>
          {ACTIONS.format(card=8)}
        </div>
      </article>
"""


def day(label, when):
    return f'      <div class="day reveal"><span class="day-n">{label}</span><span class="day-d">{when}</span></div>\n'


def events_section(heading, sub, days):
    body = "\n".join(day(label, when) + "\n".join(items) for label, when, items in days)
    return f"""<section class="events section" id="events">
  <div class="wrap">
    <div class="center head">
      <p class="eyebrow reveal">The celebration</p>
      <h2 class="script reveal">{heading}</h2>
      <p class="sub reveal">{sub}</p>
    </div>

    <div class="timeline">
      <div class="tl-line" aria-hidden="true"><span id="tlFill"></span></div>

{body}
    </div>
  </div>
</section>"""


def marquee(words):
    spans = "<b>✦</b>".join(f"<span>{w}</span>" for w in words) + "<b>✦</b>"
    return f"""<div class="marquee" aria-hidden="true">
  <div class="marquee-track">
    {spans}
    {spans}
  </div>
</div>"""


def venue_section(h2, para, items):
    rows = "\n".join(f"        <li><b>{a}</b> {b}</li>" for a, b in items)
    q = "Shree+Ram+International+Jodhpur"
    return f"""<section class="venue section" id="venue">
  <div class="wrap venue-grid">
    <div class="venue-copy">
      <p class="eyebrow reveal">The venue</p>
      <h2 class="script reveal">{h2}</h2>
      <p class="body-lg reveal">{para}</p>
      <ul class="venue-list reveal">
{rows}
      </ul>
      <a class="btn btn-ink reveal" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query={q}"><span>Open directions</span></a>
    </div>
    <div class="map reveal-card">
      <iframe title="Map of Shree Ram International, Jodhpur" referrerpolicy="no-referrer-when-downgrade" data-src="https://maps.google.com/maps?q={q}&output=embed"></iframe>
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------- themes
def rgb(hexcolor):
    h = hexcolor.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def palette(ink, ink_soft, footer, deep, mid, sage, mist, mist_light, cream, paper, blush, rose, rose_deep, ev_main, gold=None):
    """Map the full-card (green/gold) colours onto a new palette."""
    pairs = [
        ("#1d3a35", ink), ("rgba(29, 58, 53", f"rgba({rgb(ink)}"), ("rgba(29,58,53", f"rgba({rgb(ink)}"),
        ("#3f5a54", ink_soft), ("#14292a", footer),
        ("rgba(18,40,36", f"rgba({rgb(deep)}"), ("rgba(12,26,24", f"rgba({rgb(mid)}"),
        ("#dbe7e1", sage), ("#c6d8d0", mist), ("rgba(198,216,208", f"rgba({rgb(mist)}"), ("#e8f0ec", mist_light),
        ("#fbf8f1", cream), ("rgba(251,248,241", f"rgba({rgb(cream)}"), ("#f4f1e8", paper),
        ("#f2d8d6", blush), ("rgba(242,216,214", f"rgba({rgb(blush)}"),
        ("#b5264f", rose), ("--rose-deep: #5a1030", f"--rose-deep: {rose_deep}"), ("#f6efe0", ev_main),
    ]
    if gold:
        g, g_dark, g_light, g_pale, g_deep, g_mid, g_shade, g_bright = gold
        pairs += [
            ("#b08d3e", g), ("rgba(176,141,62", f"rgba({rgb(g)}"), ("#9c7a2e", g_dark), ("#e9d28f", g_light),
            ("#f0dc9f", g_pale), ("#e3c982", g_light), ("rgba(227,201,130", f"rgba({rgb(g_light)}"),
            ("#7d5f1e", g_deep), ("#c49a3c", g_mid), ("#8a6a22", g_shade), ("#d2aa4e", g_bright),
        ]
    return pairs


def themed_css(pairs):
    css = SRC_CSS
    for old, new in pairs:
        css = css.replace(old, new)
    return css


NIGHT = palette(  # Sangeet: midnight navy, crimson and gold (matches the Sangeet card)
    ink="#0e1b3d", ink_soft="#4a5578", footer="#070f26", deep="#070e26", mid="#050a1c",
    sage="#e3e6f2", mist="#c9cfe6", mist_light="#eef0f9", cream="#fbf7ee", paper="#f3efe6",
    blush="#f3d6d6", rose="#9e1b32", rose_deep="#6e0f22", ev_main="#f6efe0")

ROYAL = palette(  # Sangeet & Wedding: royal maroon and gold
    ink="#4a0e1a", ink_soft="#7a4650", footer="#2e0810", deep="#2e0810", mid="#240609",
    sage="#f4e1d6", mist="#ebc9b8", mist_light="#f9ece4", cream="#fffaf2", paper="#f8eee2",
    blush="#f6d4d4", rose="#b3122f", rose_deep="#4e0a1a", ev_main="#fbeedd",
    gold=("#b8842a", "#9a6a18", "#ecc97a", "#f4d994", "#7a5210", "#c9962f", "#8a5e14", "#d8a63e"))

SUNRISE = palette(  # 1st & 2nd December: marigold and saffron
    ink="#5a2d0c", ink_soft="#8a5a32", footer="#2f1807", deep="#2f1807", mid="#261204",
    sage="#fbe8c4", mist="#f6d08e", mist_light="#fdf1d8", cream="#fffbf0", paper="#fcf2dc",
    blush="#fbdcc6", rose="#b8321a", rose_deep="#7a2a0e", ev_main="#fdf0d2",
    gold=("#c7701a", "#a85a10", "#f8d48f", "#fbe3a8", "#8a3f06", "#d98524", "#9a4d0c", "#e89a3a"))


# ---------------------------------------------------------------- variants
VARIANTS = {
    "sangeet": dict(
        theme=NIGHT,
        title="Sangeet | Rohit &amp; Saloni",
        desc="You are invited to the Sangeet of Rohit &amp; Saloni — Tuesday 1 December 2026, 7:30 PM onwards, Utsav Lawn, Shree Ram International, Jodhpur.",
        theme_color="#0e1b3d",
        first="2026-12-01T19:30:00+05:30",
        body_extra=' data-fx="lights" data-particles="notes"',
        gate="cards/card-6.jpg", gate_alt="Rohit and Saloni Sangeet invitation",
        hero_wide="img/hill.jpg", hero_tall="img/run.jpg", hero_alt="Rohit and Saloni running hand in hand at golden hour",
        mantra_small="A night of music, dance &amp; celebration",
        hero_date="<span>Tue</span><i></i><span>01 Dec</span> <em>2026</em>",
        hero_place="Utsav Lawn · Shree Ram International, Jodhpur",
        count_note="until the Sangeet begins",
        marquee=["Sangeet", "Music", "Dance", "Celebration", "Sangeet Night"],
        invite_line="cordially solicits your gracious presence on the Sangeet ceremony of her beloved grandson",
        events=events_section("The Sangeet", "An evening of music, dance and dinner. Tap the card to see the invitation.",
                              [("The Evening", "Tuesday · 1 December 2026", [SANGEET])]),
        venue=venue_section("Utsav Lawn", "Join us at Utsav Lawn, Shree Ram International, Jodhpur, for a night of music, dance and dinner under the stars.",
                            [("Utsav Lawn", "Sangeet · 7:30 PM onwards")]),
        song_file="audio/sangeet.mp3", song_title="Sangeet Song",
        fairy=True,
    ),
    "sangeet-wedding": dict(
        theme=ROYAL,
        title="Sangeet &amp; Wedding | Rohit &amp; Saloni",
        desc="You are invited to the Sangeet (1 December) and the wedding (2 December 2026) of Rohit &amp; Saloni, Shree Ram International, Jodhpur.",
        theme_color="#4a0e1a",
        first="2026-12-01T19:30:00+05:30",
        body_extra="",
        gate="cards/card-8.jpg", gate_alt="Rohit and Saloni wedding invitation",
        hero_wide="img/sunset.jpg", hero_tall="img/lake.jpg", hero_alt="Rohit and Saloni laughing together by the lake",
        mantra_small="Sangeet &amp; Wedding · Two evenings of celebration",
        hero_date="<span>01 Dec</span><i></i><span>02 Dec</span> <em>2026</em>",
        hero_place="Shree Ram International, Jodhpur",
        count_note="until the Sangeet begins",
        marquee=["Sangeet", "Baraat", "Reception", "Wedding", "Phere"],
        invite_line="cordially solicits your gracious presence at the Sangeet and the wedding of her beloved grandson",
        events=events_section("Sangeet &amp; Wedding", "Two evenings of celebration. Tap a card to see the invitation.",
                              [("Day One", "Tuesday · 1 December 2026", [SANGEET]),
                               ("Day Two", "Wednesday · 2 December 2026", [WEDDING])]),
        venue=venue_section("Shree Ram <br>International", "The Sangeet and the Reception unfold at Utsav Lawn, Shree Ram International, Jodhpur. The Baraat sets out from the residence “Satyam”.",
                            [("Utsav Lawn", "Sangeet &amp; Reception"), ("Residence “Satyam”", "Baraat departure")]),
        song_file=None, song_title=None, fairy=False,
    ),
    "dec-1-2": dict(
        theme=SUNRISE,
        title="1st &amp; 2nd December | Rohit &amp; Saloni",
        desc="Celebrations of Rohit &amp; Saloni on 1st and 2nd December 2026 — Carnival of Love, Tilak, Sangeet, Mayra and the Wedding, Shree Ram International, Jodhpur.",
        theme_color="#5a2d0c",
        first="2026-12-01T10:15:00+05:30",
        body_extra="",
        gate="cards/card-1.jpg", gate_alt="Rohit and Saloni wedding invitation cover",
        hero_wide="img/p8.jpg", hero_tall="img/carry.jpg", hero_alt="Rohit lifting Saloni into his arms below a rocky hill",
        mantra_small="Two days of celebration",
        hero_date="<span>01 Dec</span><i></i><span>02 Dec</span> <em>2026</em>",
        hero_place="Shree Ram International, Jodhpur",
        count_note="until the celebrations begin",
        marquee=["Carnival of Love", "Tilak", "Sangeet", "Mayra", "Wedding"],
        invite_line="cordially solicits your gracious presence at the celebrations of the wedding of her beloved grandson on the 1st &amp; 2nd of December",
        events=events_section("Wedding Events", "Full-day celebrations across the 1st &amp; 2nd of December. Tap any card to see the invitation.",
                              [("Day One", "Tuesday · 1 December 2026", [CARNIVAL, TILAK, SANGEET]),
                               ("Day Two", "Wednesday · 2 December 2026", [MAYRA, WEDDING])]),
        venue=None, song_file=None, song_title=None, fairy=False,
    ),
}

ROOT_INVITE = "cordially solicits your gracious presence on the auspicious occasion of the wedding of her beloved grandson"


def build(slug, v):
    html = SRC_HTML
    url = f"{BASE_URL}/{slug}/"
    html = swap_re(html, r"<title>.*?</title>", f"<title>{v['title']}</title>")
    html = swap_re(html, r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{v["desc"]}">')
    html = swap_re(html, r'<meta name="theme-color" content="[^"]*">', f'<meta name="theme-color" content="{v["theme_color"]}">')
    html = swap_re(html, r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{v["title"]}">')
    html = swap_re(html, r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{v["desc"]}">')
    html = swap_re(html, r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">')

    html = swap(html, '<body class="locked">',
                f'<body class="locked" data-root="../" data-first="{v["first"]}"{v["body_extra"]}>')
    html = swap_re(html, r'src="cards/card-1\.jpg" alt="[^"]*"', f'src="{v["gate"]}" alt="{v["gate_alt"]}"')

    html = swap_re(html, r'srcset="img/main-wide\.jpg"', f'srcset="{v["hero_wide"]}"')
    html = swap_re(html, r'src="img/main\.jpg" alt="[^"]*"', f'src="{v["hero_tall"]}" alt="{v["hero_alt"]}"')
    html = swap_re(html, r'<p class="mantra small reveal-h">.*?</p>', f'<p class="mantra small reveal-h">{v["mantra_small"]}</p>')
    html = swap_re(html, r'<p class="hero-date reveal-h">.*?</p>', f'<p class="hero-date reveal-h">{v["hero_date"]}</p>')
    html = swap_re(html, r'<p class="hero-place reveal-h">.*?</p>', f'<p class="hero-place reveal-h">{v["hero_place"]}</p>')
    html = swap(html, "until the celebrations begin", v["count_note"])
    if v["fairy"]:
        html = swap(html, '<div class="hero-shade"></div>', '<div class="hero-shade"></div>\n  <div class="fairy" aria-hidden="true"></div>')

    html = swap_block(html, "MARQUEE", marquee(v["marquee"]))
    html = swap(html, ROOT_INVITE, v["invite_line"])
    html = swap_block(html, "EVENTS", v["events"])
    if v["venue"]:
        html = swap_block(html, "VENUE", v["venue"])
    if v["song_file"]:
        html = swap(html, 'src="audio/song.mp3"', f'src="{v["song_file"]}"')
        html = swap(html, "<b>Perfect</b>", f'<b>{v["song_title"]}</b>')
        html = swap(html, 'id="songTitle">Perfect<', f'id="songTitle">{v["song_title"]}<')

    # the variant lives one folder down: point shared assets at the parent folder
    html = re.sub(r'(src|srcset|data-lb|href)="(img|cards|audio)/', r'\1="../\2/', html)
    html = html.replace('href="favicon.svg"', 'href="../favicon.svg"').replace('src="script.js"', 'src="../script.js"')

    out = SITE / slug
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / "style.css").write_text(themed_css(v["theme"]), encoding="utf-8")
    print(f"built {slug}/  ({len(html.splitlines())} lines)")


if __name__ == "__main__":
    for name, spec in VARIANTS.items():
        build(name, spec)

#!/usr/bin/env python3
"""Draws the mountain pictures used on the site. Plain SVG, no external files."""
import random, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "img")
W, H = 800, 560


def walk(rng, x0, y0, x1, y1, steps, jag):
    """jagged line between two points"""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + rng.uniform(-jag, jag) * (1 - abs(0.5 - t) * 0.6)
        pts.append((x, y))
    return pts


def poly(pts, fill, extra=""):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{d}" fill="{fill}" {extra}/>'


def ridge(rng, base_y, amp, color, w=W, step=40, opacity=1):
    pts = [(-20, H + 10)]
    x = -20
    while x < w + 40:
        pts.append((x, base_y - rng.uniform(0, amp) - math.sin(x / 90) * amp * 0.3))
        x += step + rng.uniform(-10, 10)
    pts.append((w + 40, H + 10))
    return poly(pts, color, f'opacity="{opacity}"')


def peak(rng, sx, sy, spread, base, c, uid, snow_y, jag=14):
    left = walk(rng, sx, sy, sx - spread, base, 14, jag)
    right = walk(rng, sx, sy, sx + spread * 0.95, base, 14, jag)
    face = walk(rng, sx, sy, sx + rng.uniform(-30, 30), base, 14, jag * 0.8)
    lit = left + face[::-1]
    shade = face + right[1:][::-1][::-1]
    shade = face + right[1:]
    shade = shade + [(sx + spread * 0.95, base + 5), (sx, base + 5)]
    lit = lit + [(sx, base + 5), (sx - spread, base + 5)]
    out = [poly(lit, c["lit"]), poly(shade, c["shade"])]
    # couloirs / rock texture
    for _ in range(9):
        t = rng.uniform(0.15, 0.9)
        side = rng.choice([left, right])
        bx, by = side[int(t * 13)]
        ex = bx + rng.uniform(-12, 12)
        ey = by + rng.uniform(30, 90)
        out.append(
            f'<path d="M{bx:.1f} {by:.1f} L{ex:.1f} {ey:.1f}" stroke="{c["shade"]}" stroke-width="{rng.uniform(1,2.4):.1f}" opacity=".45" fill="none"/>'
        )
    # snow on top of the same shapes, clipped by a ragged snow line
    sl = [(-20, 0), (W + 20, 0)]
    xs = list(range(W + 20, -21, -25))
    for x in xs:
        sl.append((x, snow_y + rng.uniform(-28, 28) + abs(x - sx) * 0.08))
    cid = f"sn{uid}"
    out.insert(0, f'<clipPath id="{cid}">{poly(sl, "#000")}</clipPath>')
    out.append(f'<g clip-path="url(#{cid})">{poly(lit, c["snowlit"])}{poly(shade, c["snowshade"])}</g>')
    return "\n".join(out), left, right


def sky(c, uid, stars=False, rng=None, aurora=False):
    s = f'<defs><linearGradient id="sk{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["sky0"]}"/><stop offset="1" stop-color="{c["sky1"]}"/></linearGradient></defs>'
    s += f'<rect width="{W}" height="{H}" fill="url(#sk{uid})"/>'
    if stars:
        for _ in range(110):
            s += f'<circle cx="{rng.uniform(0,W):.0f}" cy="{rng.uniform(0,H*0.55):.0f}" r="{rng.choice([.6,.8,1,1.3]):.1f}" fill="#fff" opacity="{rng.uniform(.35,.95):.2f}"/>'
    if aurora:
        for i, col in enumerate(["#4cf0a8", "#38c6d9", "#8b7bff"]):
            y = 120 + i * 38
            s += f'<path d="M-20 {y} C 150 {y-70}, 300 {y+60}, 450 {y-30} S 700 {y+40}, 830 {y-40} L830 {y+60} C 700 {y+120}, 550 {y+10}, 400 {y+80} S 120 {y+30}, -20 {y+90} Z" fill="{col}" opacity=".18"/>'
    return s


def sun(x, y, r, col, glow):
    return (
        f'<circle cx="{x}" cy="{y}" r="{r*3.2}" fill="{glow}" opacity=".18"/>'
        f'<circle cx="{x}" cy="{y}" r="{r*1.9}" fill="{glow}" opacity=".28"/>'
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>'
    )


def mist(y, col, op=0.35):
    return f'<rect x="-10" y="{y}" width="{W+20}" height="70" fill="{col}" opacity="{op}" style="filter:blur(14px)"/>'


def pines(rng, n, y, col, h=(40, 90)):
    out = []
    for _ in range(n):
        x = rng.uniform(-10, W + 10)
        hh = rng.uniform(*h)
        w = hh * 0.34
        out.append(poly([(x, y - hh), (x - w, y), (x + w, y)], col))
        out.append(poly([(x, y - hh * 0.72), (x - w * 1.2, y - hh * 0.18), (x + w * 1.2, y - hh * 0.18)], col))
    return "".join(out)


def climbers(rng, pts, n, col="#0b1220", scale=1.0):
    """little rope team walking along ridge points"""
    out = []
    start = rng.randint(2, max(2, len(pts) - n - 2))
    prev = None
    for i in range(n):
        x, y = pts[start + i]
        x += 3
        out.append(f'<ellipse cx="{x:.1f}" cy="{y-6*scale:.1f}" rx="{2.1*scale:.1f}" ry="{4.4*scale:.1f}" fill="{col}"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y-12*scale:.1f}" r="{1.8*scale:.1f}" fill="{col}"/>')
        if prev:
            out.append(f'<path d="M{prev[0]:.1f} {prev[1]-5*scale:.1f} L{x:.1f} {y-5*scale:.1f}" stroke="{col}" stroke-width=".7" opacity=".7"/>')
        prev = (x, y)
    return "".join(out)


def flags(x0, y0, x1, y1, n=9):
    cols = ["#3b82f6", "#f8fafc", "#ef4444", "#22c55e", "#facc15"]
    out = [f'<path d="M{x0} {y0} Q {(x0+x1)/2} {max(y0,y1)+26} {x1} {y1}" stroke="#2b2b2b" stroke-width="1.4" fill="none"/>']
    for i in range(n):
        t = (i + .5) / n
        x = x0 + (x1 - x0) * t
        y = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * (max(y0, y1) + 26) + t * t * y1
        out.append(poly([(x - 9, y), (x + 9, y), (x + 9, y + 18), (x - 9, y + 18)], cols[i % 5], 'opacity=".92"'))
    return "".join(out)


def svg(body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" role="img" aria-label="{title}">'
        f"<title>{title}</title>{body}</svg>"
    )


PAL = {
    "dawn": dict(sky0="#2a2f6b", sky1="#f6a46a", far="#8a7fb0", mid="#5d5b8f", lit="#d98d6c", shade="#4a3f6b", snowlit="#fff1e4", snowshade="#b7b4d9", mist="#ffd8b8", sun="#fff3c4", glow="#ffb56b", fg="#1b1730"),
    "noon": dict(sky0="#2f7fc4", sky1="#cfe9f7", far="#9db8d3", mid="#6f8caa", lit="#8f9aa6", shade="#4c5a69", snowlit="#ffffff", snowshade="#bcd0e6", mist="#ffffff", sun="#fffbe6", glow="#fff", fg="#1e2f3a"),
    "storm": dict(sky0="#1c2330", sky1="#5a6676", far="#59647a", mid="#3d4659", lit="#6a7380", shade="#2b3340", snowlit="#e6ecf3", snowshade="#8d9bb0", mist="#cfd8e3", sun="#cdd6e2", glow="#cdd6e2", fg="#10151d"),
    "dusk": dict(sky0="#23224f", sky1="#e8708a", far="#7c5a93", mid="#503d73", lit="#c7708a", shade="#36274f", snowlit="#ffe2ea", snowshade="#a98bc4", mist="#ffc1c9", sun="#ffe7b8", glow="#ff9aa8", fg="#150f24"),
    "night": dict(sky0="#050914", sky1="#13233f", far="#1e2f4d", mid="#16233b", lit="#33486a", shade="#0d172a", snowlit="#b9d3f5", snowshade="#587aa9", mist="#3a5a88", sun="#f3f6ff", glow="#9db9ff", fg="#04070e"),
    "gold": dict(sky0="#1d6a8a", sky1="#ffe3a1", far="#7fb0b5", mid="#4f8a8c", lit="#d6a15f", shade="#7a5a3e", snowlit="#fffdf3", snowshade="#c9d8e0", mist="#fff0c8", sun="#fff7d6", glow="#ffd37a", fg="#1a2a22"),
}


def scene(name, title, pal, seed, sx, sy, spread, snow_y, sun_xy=None, extra="", stars=False, aurora=False, foreground="pines", team=True, moon=False):
    rng = random.Random(seed)
    c = PAL[pal]
    b = sky(c, name, stars, rng, aurora)
    if sun_xy:
        b += sun(sun_xy[0], sun_xy[1], 22, c["sun"], c["glow"])
    b += ridge(rng, 400, 90, c["far"], opacity=.9)
    # second small summit behind
    pk2, _, _ = peak(rng, sx - 250 if sx > 400 else sx + 270, sy + 110, 170, 470, dict(lit=c["far"], shade=c["mid"], snowlit=c["snowlit"], snowshade=c["snowshade"]), name + "b", snow_y + 90, 9)
    b += pk2
    b += mist(330, c["mist"], .35)
    pk, left, right = peak(rng, sx, sy, spread, 500, c, name + "a", snow_y)
    b += pk
    if team:
        b += climbers(rng, right if rng.random() > .5 else left, 4, c["fg"])
    b += mist(420, c["mist"], .45)
    b += ridge(rng, 500, 40, c["mid"], step=55)
    if foreground == "pines":
        b += pines(rng, 26, H + 6, c["fg"])
    elif foreground == "rocks":
        for _ in range(7):
            x = rng.uniform(0, W)
            w = rng.uniform(60, 150)
            b += poly([(x, H), (x + w * .2, H - w * .35), (x + w * .6, H - w * .42), (x + w, H)], c["fg"])
    b += extra
    return svg(b, title)


def hut():
    rng = random.Random(7)
    c = PAL["night"]
    b = sky(c, "hut", True, rng, False)
    b += sun(640, 110, 16, c["sun"], c["glow"])
    b += ridge(rng, 380, 100, c["far"])
    pk, left, right = peak(rng, 420, 120, 330, 520, c, "hutp", 300)
    b += pk
    b += mist(430, c["mist"], .3)
    b += ridge(rng, 520, 30, c["shade"], step=50)
    # the hut
    b += poly([(250, 470), (250, 400), (330, 360), (410, 400), (410, 470)], "#2a1d17")
    b += poly([(240, 402), (330, 350), (420, 402), (410, 410), (330, 365), (250, 410)], "#4d6a8c")
    b += '<rect x="285" y="415" width="26" height="22" fill="#ffd36e"/><rect x="345" y="415" width="26" height="22" fill="#ffd36e"/>'
    b += '<circle cx="298" cy="426" r="48" fill="#ffd36e" opacity=".12"/><circle cx="358" cy="426" r="48" fill="#ffd36e" opacity=".12"/>'
    b += '<rect x="318" y="440" width="22" height="30" fill="#17100c"/>'
    b += poly([(230, 470), (430, 470), (470, H), (190, H)], "#cfe0f5", 'opacity=".9"')
    b += rect_fg(c["fg"])
    return svg(b, "A mountain hut glowing under the stars")


def rect_fg(col):
    return f'<rect x="0" y="{H-18}" width="{W}" height="22" fill="{col}"/>'


def camp():
    rng = random.Random(21)
    c = PAL["dusk"]
    b = sky(c, "camp", True, rng, False)
    b += ridge(rng, 360, 110, c["far"])
    pk, left, right = peak(rng, 540, 130, 300, 500, c, "campp", 290)
    b += pk
    b += mist(400, c["mist"], .4)
    b += poly([(-20, 470), (200, 450), (500, 462), (830, 448), (830, H), (-20, H)], "#d9c9e4")
    for i, (x, y, s) in enumerate([(130, 505, 1.2), (290, 490, 1.0), (440, 512, 1.35), (610, 495, 1.05)]):
        col = ["#ef6a3a", "#f7b733", "#3aa0ef", "#ef6a3a"][i]
        b += poly([(x - 48 * s, y), (x, y - 40 * s), (x + 48 * s, y)], col)
        b += poly([(x, y - 40 * s), (x + 48 * s, y), (x + 8 * s, y)], "#0000001f")
        b += f'<path d="M{x-10*s} {y} L{x} {y-18*s} L{x+10*s} {y}" fill="#2a1a12" opacity=".85"/>'
        b += f'<circle cx="{x}" cy="{y-8*s}" r="{34*s}" fill="#ffd36e" opacity=".10"/>'
    b += rect_fg(c["fg"])
    return svg(b, "Tents at a high camp at dusk")


def ice():
    rng = random.Random(31)
    b = f'<rect width="{W}" height="{H}" fill="#cfe8f6"/><defs><linearGradient id="ig" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e9f7ff"/><stop offset=".55" stop-color="#8cc7e8"/><stop offset="1" stop-color="#2f78a6"/></linearGradient></defs>'
    b += f'<rect width="{W}" height="{H}" fill="url(#ig)"/>'
    for i in range(7):
        x = 60 + i * 115 + rng.uniform(-20, 20)
        h = rng.uniform(260, 470)
        b += f'<path d="M{x} 0 L{x+rng.uniform(-14,14)} {h*.35} L{x+rng.uniform(-18,18)} {h*.7} L{x+rng.uniform(-12,12)} {h} L{x+22} {h} L{x+22+rng.uniform(-10,10)} 0 Z" fill="#fff" opacity="{rng.uniform(.25,.55):.2f}"/>'
        b += f'<path d="M{x+22} 0 L{x+22} {h}" stroke="#2f78a6" opacity=".25"/>'
    for _ in range(40):
        x = rng.uniform(0, W); y = rng.uniform(0, H)
        b += f'<path d="M{x:.0f} {y:.0f} l{rng.uniform(-40,40):.0f} {rng.uniform(10,50):.0f}" stroke="#fff" stroke-width="1" opacity=".5"/>'
    # climber
    b += '<g fill="#10213a" stroke="#10213a"><circle cx="420" cy="180" r="11"/><path d="M420 191 L416 250 L404 310 M420 191 L418 250 L440 300 M418 205 L392 168 M418 205 L452 150" stroke-width="9" stroke-linecap="round" fill="none"/><path d="M452 150 l-3 -28" stroke="#c9d6e2" stroke-width="3"/><path d="M392 168 l-4 -26" stroke="#c9d6e2" stroke-width="3"/></g>'
    b += '<path d="M420 205 C 470 300, 380 400, 430 560" stroke="#f59e0b" stroke-width="2.2" fill="none"/>'
    return svg(b, "Ice climber on a frozen waterfall")


def crevasse():
    rng = random.Random(41)
    c = PAL["noon"]
    b = sky(c, "crev", False, rng)
    b += ridge(rng, 330, 80, c["far"])
    b += ridge(rng, 380, 40, c["mid"], step=60)
    b += poly([(-20, 360), (830, 340), (830, H), (-20, H)], "#f1f8ff")
    # crevasse
    b += poly([(120, 470), (300, 430), (520, 445), (700, 420), (690, 450), (520, 480), (300, 470), (140, 515)], "#1d4f7a")
    b += poly([(180, 478), (310, 452), (520, 464), (640, 445), (610, 462), (520, 472), (310, 468), (190, 495)], "#0b2a47")
    # rope team
    x = 150
    pts = []
    for i in range(4):
        px, py = 160 + i * 62, 420 - i * 6
        pts.append((px, py))
        b += f'<ellipse cx="{px}" cy="{py-14}" rx="5" ry="11" fill="#c8242b"/><circle cx="{px}" cy="{py-30}" r="4.4" fill="#10213a"/>'
        b += f'<path d="M{px} {py-4} l-3 16 M{px} {py-4} l5 16" stroke="#10213a" stroke-width="3"/>'
    for a, d in zip(pts, pts[1:]):
        b += f'<path d="M{a[0]} {a[1]-14} Q {(a[0]+d[0])/2} {a[1]-4} {d[0]} {d[1]-14}" stroke="#222" stroke-width="1" fill="none"/>'
    b += '<path d="M700 300 l-4 40" stroke="#333" stroke-width="2"/>' + poly([(700, 300), (730, 308), (700, 318)], "#ef4444")
    return svg(b, "A rope team crossing a glacier")


def prayer():
    rng = random.Random(51)
    c = PAL["gold"]
    b = sky(c, "pray", False, rng)
    b += sun(210, 190, 26, c["sun"], c["glow"])
    b += ridge(rng, 360, 100, c["far"])
    pk, left, right = peak(rng, 560, 110, 300, 500, c, "prayp", 300)
    b += pk
    b += mist(410, c["mist"], .45)
    b += ridge(rng, 520, 35, c["mid"], step=50)
    b += poly([(-20, 480), (830, 470), (830, H), (-20, H)], "#2c2418")
    b += '<rect x="108" y="290" width="6" height="200" fill="#2a2018"/><rect x="690" y="270" width="6" height="220" fill="#2a2018"/>'
    b += flags(111, 296, 693, 280, 17) + flags(111, 330, 693, 322, 17)
    return svg(b, "Prayer flags above a Himalayan valley")


def savanna():
    rng = random.Random(61)
    c = PAL["dawn"]
    b = sky(c, "kili", False, rng)
    b += sun(180, 330, 28, c["sun"], c["glow"])
    # wide flat topped volcano
    pts = [(-20, 470), (140, 400), (300, 300), (390, 262), (470, 250), (560, 262), (690, 330), (830, 410), (830, 520), (-20, 520)]
    b += poly(pts, c["mid"])
    b += poly([(300, 300), (390, 262), (470, 250), (520, 270), (440, 290), (360, 296)], "#fff5ea")
    b += poly([(470, 250), (560, 262), (690, 330), (830, 410), (830, 520), (520, 520), (500, 380)], c["shade"], 'opacity=".55"')
    b += mist(380, c["mist"], .4)
    b += poly([(-20, 470), (830, 465), (830, H), (-20, H)], "#2a1c20")
    # acacia
    b += '<path d="M600 540 L600 470 M600 490 L570 470 M600 485 L640 462" stroke="#120a0d" stroke-width="5" fill="none"/><ellipse cx="600" cy="452" rx="92" ry="17" fill="#120a0d"/><ellipse cx="548" cy="467" rx="46" ry="10" fill="#120a0d"/>'
    return svg(b, "Kilimanjaro at sunrise over the savanna")


def old():
    """sepia drawing for the history section"""
    rng = random.Random(77)
    pal = dict(sky0="#e8d9b5", sky1="#f4ead0", far="#c9b48a", mid="#a98f62", lit="#cdb98f", shade="#8a7248", snowlit="#fbf5e3", snowshade="#d6c9a5", mist="#f4ead0", fg="#4a3b20")
    PAL["sepia"] = dict(pal, sun="#fff", glow="#fff")
    return scene("sepia", "Old style engraving of a high alpine peak", "sepia", 77, 430, 110, 300, 290, None, foreground="rocks", team=True)


def logo():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><title>Alpine Ascents logo</title>'
        '<rect width="64" height="64" rx="14" fill="#0f2233"/>'
        '<polygon points="6,50 24,18 33,34 40,24 58,50" fill="#e9f3f8"/>'
        '<polygon points="24,18 33,34 28,34 24,27 20,34 15,34" fill="#9cc4d9" opacity=".0"/>'
        '<polygon points="24,18 29,27 24,25 19,28" fill="#ffffff"/>'
        '<polygon points="40,24 44,31 40,29.5 36,31.5" fill="#fff"/>'
        '<circle cx="48" cy="15" r="5" fill="#f0743e"/></svg>'
    )


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    items = {
        "everest-dawn": scene("a", "Everest massif at dawn", "dawn", 3, 400, 90, 330, 300, (130, 170)),
        "k2-storm": scene("b", "K2 in a building storm", "storm", 11, 470, 80, 300, 270, None, team=True, foreground="rocks"),
        "matterhorn-noon": scene("c", "Matterhorn style pyramid peak in clear weather", "noon", 19, 400, 70, 230, 330, (680, 110)),
        "denali-aurora": scene("d", "Denali under the northern lights", "night", 27, 380, 100, 330, 280, (660, 90), stars=True, aurora=True),
        "aconcagua-dusk": scene("e", "Aconcagua at dusk", "dusk", 35, 450, 110, 320, 300, (140, 250), stars=False),
        "summit-ridge": scene("f", "Climbers on a summit ridge", "gold", 43, 330, 120, 300, 310, (680, 140), foreground="rocks"),
        "kilimanjaro": savanna(),
        "high-camp": camp(),
        "mountain-hut": hut(),
        "ice-climbing": ice(),
        "glacier-team": crevasse(),
        "prayer-flags": prayer(),
        "history-engraving": old(),
    }
    for k, v in items.items():
        open(f"{OUT}/{k}.svg", "w", encoding="utf-8").write(v)
    open(f"{OUT}/logo.svg", "w").write(logo())
    open(os.path.join(HERE, "..", "favicon.svg"), "w").write(logo())
    print(len(items) + 1, "images written")

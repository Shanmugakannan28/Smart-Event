"""Generates the event banner illustrations (SVG, 16:9) into backend/static/banners.
Run:  python tools/make_banners.py     (only needed if you want to tweak the artwork)"""
import math, random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "static" / "banners"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1200, 675


def svg(defs, body, w=W, h=H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice">'
            f'<defs>{defs}</defs>{body}</svg>')


def lg(id_, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


GLOW = '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'


def stars(r, n, ymax, color="#fff"):
    return "".join(f'<circle cx="{r.randint(0,W)}" cy="{r.randint(0,ymax)}" r="{r.choice([1,1.5,2,2.5])}" fill="{color}" opacity="{r.uniform(.4,1):.2f}"/>' for _ in range(n))


def sunset_beats():
    r = random.Random(1)
    d = lg("sky", [(0, "#1b0b3a"), (.4, "#6a1b9a"), (.72, "#ff5e7e"), (1, "#ffb74d")]) + \
        '<radialGradient id="sun"><stop offset="0" stop-color="#fff3c4"/><stop offset="1" stop-color="#ff8a5c"/></radialGradient>'
    b = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>' + stars(r, 60, 230)
    b += '<circle cx="600" cy="400" r="170" fill="url(#sun)"/>'
    for i in range(7):  # sun stripes
        y = 380 + i * 22
        b += f'<rect x="420" y="{y}" width="360" height="{3+i*1.6}" fill="#ff5e7e" opacity=".85"/>'
    b += f'<rect y="470" width="{W}" height="205" fill="#1a0b30"/>'
    for i in range(0, W, 24):  # equalizer skyline
        h = 40 + abs(math.sin(i * .021)) * 120 + r.randint(0, 60)
        b += f'<rect x="{i}" y="{470-h:.0f}" width="16" height="{h+4:.0f}" rx="8" fill="#1a0b30"/>'
    for i in range(0, W, 24):  # crowd dots
        b += f'<circle cx="{i+8}" cy="{560+r.randint(0,90)}" r="{r.randint(14,24)}" fill="#0d0520"/>'
    for x in (150, 1050):  # stage lights
        b += f'<polygon points="{x},0 {x-90},420 {x+90},420" fill="#fff" opacity=".07"/>'
    return svg(d, b)


def tech_summit():
    r = random.Random(2)
    d = lg("bg", [(0, "#071a33"), (1, "#0e5766")], 1, 1) + GLOW + \
        '<pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.6" fill="#5ce1e6" opacity=".25"/></pattern>'
    b = f'<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#dots)"/>'
    pts = [(r.randint(40, W-40), r.randint(40, H-40)) for _ in range(26)]
    for i, p in enumerate(pts):
        near = sorted(pts, key=lambda q: (q[0]-p[0])**2 + (q[1]-p[1])**2)[1:3]
        for q in near:
            b += f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="#5ce1e6" opacity=".22"/>'
    for p in pts:
        b += f'<circle cx="{p[0]}" cy="{p[1]}" r="{r.choice([4,5,7])}" fill="#5ce1e6" opacity=".7"/>'
    b += '<g filter="url(#glow)" stroke="#8ff5ff" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" fill="none">' \
         '<polyline points="430,240 330,338 430,436"/><polyline points="770,240 870,338 770,436"/><line x1="640" y1="215" x2="560" y2="460"/></g>'
    b += '<rect x="250" y="520" width="700" height="14" rx="7" fill="#5ce1e6" opacity=".35"/><rect x="250" y="548" width="460" height="14" rx="7" fill="#5ce1e6" opacity=".2"/>'
    return svg(d, b)


def marathon():
    r = random.Random(3)
    d = lg("sky", [(0, "#38a3e8"), (1, "#d7f0ff")]) + lg("trk", [(0, "#c44a22"), (1, "#a8381a")]) + \
        '<radialGradient id="sun"><stop offset="0" stop-color="#fff9d6"/><stop offset="1" stop-color="#ffe27a"/></radialGradient>'
    b = f'<rect width="{W}" height="{H}" fill="url(#sky)"/><circle cx="930" cy="170" r="70" fill="url(#sun)"/>'
    b += '<path d="M0 300 Q200 230 420 290 T820 270 T1200 300 V330 H0Z" fill="#5fb06a"/><path d="M0 320 Q300 270 600 315 T1200 310 V340 H0Z" fill="#3f9150"/>'
    b += f'<rect y="330" width="{W}" height="345" fill="#3f9150"/>'
    b += '<polygon points="570,330 630,330 1450,675 -250,675" fill="url(#trk)"/>'
    for k in range(-3, 4):
        x = 600 + k * 33
        xb = 600 + k * 330
        b += f'<line x1="{x}" y1="330" x2="{xb}" y2="675" stroke="#fff" stroke-width="{4 if abs(k)<3 else 5}" opacity=".9"/>'
    b += '<polygon points="540,520 660,520 700,555 500,555" fill="#fff" opacity=".0"/>'
    b += '<polygon points="470,480 730,480 760,505 440,505" fill="#fff" opacity=".85"/>'
    for i in range(14):  # bunting flags
        x = 60 + i * 85
        b += f'<polygon points="{x},60 {x+34},60 {x+17},100" fill="{r.choice(["#ff595e","#ffca3a","#8ac926","#1982c4","#fff"])}"/>'
    b += '<path d="M0 60 Q600 130 1200 60" stroke="#fff" fill="none" stroke-width="3" opacity=".7"/>'
    return svg(d, b)


def founders_meetup():
    r = random.Random(4)
    d = lg("bg", [(0, "#0c1a2b"), (.6, "#1f4260"), (1, "#e6a15c")])
    b = f'<rect width="{W}" height="{H}" fill="url(#bg)"/>' + stars(r, 30, 200)
    x = -20
    while x < W:
        w, h = r.randint(70, 130), r.randint(180, 430)
        b += f'<rect x="{x}" y="{H-h}" width="{w}" height="{h}" fill="#0a1522"/>'
        for wy in range(H - h + 18, H - 14, 26):
            for wx in range(x + 12, x + w - 14, 22):
                if r.random() < .42:
                    b += f'<rect x="{wx}" y="{wy}" width="9" height="14" fill="#ffd27a" opacity="{r.uniform(.5,1):.2f}"/>'
        x += w + r.randint(6, 18)
    pts = [(80 + i * 140, 520 - i * 38 - r.randint(-30, 30)) for i in range(9)]
    b += '<polyline points="' + " ".join(f"{a},{c}" for a, c in pts) + '" fill="none" stroke="#ffd27a" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
    for a, c in pts:
        b += f'<circle cx="{a}" cy="{c}" r="9" fill="#0a1522" stroke="#ffd27a" stroke-width="5"/>'
    return svg(d, b)


def acoustic_nights():
    r = random.Random(5)
    d = lg("bg", [(0, "#14142b"), (.7, "#3b2a55"), (1, "#7a3e5c")]) + \
        '<radialGradient id="warm"><stop offset="0" stop-color="#ffcf7a" stop-opacity=".55"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/></radialGradient>'
    b = f'<rect width="{W}" height="{H}" fill="url(#bg)"/>' + stars(r, 80, 380)
    b += '<circle cx="930" cy="170" r="260" fill="url(#warm)"/><circle cx="930" cy="170" r="70" fill="#ffe9b5"/><circle cx="955" cy="156" r="62" fill="#2c2147"/>'
    for i in range(6):  # strings
        y = 330 + i * 34
        b += f'<path d="M0 {y} C300 {y-24-i*3} 700 {y+24+i*3} 1200 {y}" stroke="#ffcf7a" stroke-width="{1.2+i*.5}" fill="none" opacity="{.85-i*.08:.2f}"/>'
    b += '<path d="M0 600 Q300 540 600 590 T1200 570 V675 H0Z" fill="#120c22"/>'
    for i in range(12):
        b += f'<circle cx="{r.randint(50,1150)}" cy="{r.randint(560,650)}" r="{r.randint(3,5)}" fill="#ffcf7a" opacity=".8"/>'  # fairy lights
    return svg(d, b)


def ai_hackathon():
    r = random.Random(6)
    d = lg("bg", [(0, "#0d0222"), (1, "#32116b")], 1, 1) + GLOW
    b = f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'
    layers = [(190, 5), (440, 7), (690, 7), (940, 4)]
    nodes = [[(x, 110 + (H - 220) * (j + .5) / n) for j in range(n)] for x, n in layers]
    for a, c in zip(nodes, nodes[1:]):
        for p in a:
            for q in c:
                b += f'<line x1="{p[0]}" y1="{p[1]:.0f}" x2="{q[0]}" y2="{q[1]:.0f}" stroke="#a78bfa" stroke-width="1.2" opacity=".28"/>'
    b += '<g filter="url(#glow)">'
    for li, col in enumerate(nodes):
        for p in col:
            b += f'<circle cx="{p[0]}" cy="{p[1]:.0f}" r="{r.choice([13,16,19])}" fill="{["#22d3ee","#a78bfa","#f472b6","#facc15"][li]}"/>'
    b += '</g>'
    return svg(d, b)


def football_cup():
    d = lg("g", [(0, "#115c2d"), (1, "#1faa52")], 0, 1) + lg("beam", [(0, "#fff"), (1, "#fff")])
    b = f'<rect width="{W}" height="{H}" fill="url(#g)"/>'
    for i in range(0, W, 150):
        b += f'<rect x="{i}" width="75" height="{H}" fill="#fff" opacity=".05"/>'
    b += '<g fill="none" stroke="#fff" stroke-width="5" opacity=".85"><rect x="70" y="60" width="1060" height="555"/><line x1="600" y1="60" x2="600" y2="615"/>' \
         '<circle cx="600" cy="337" r="95"/><rect x="70" y="205" width="170" height="265"/><rect x="960" y="205" width="170" height="265"/>' \
         '<rect x="70" y="270" width="70" height="135"/><rect x="1060" y="270" width="70" height="135"/></g><circle cx="600" cy="337" r="9" fill="#fff"/>'
    for x in (0, W):
        b += f'<polygon points="{x},0 {abs(x-380)},{H} {abs(x-760)},{H}" fill="#fff" opacity=".10"/>'
    b += '<g transform="translate(600 337)"><circle r="46" fill="#fff" stroke="#111" stroke-width="3"/><polygon points="0,-20 19,-6 12,16 -12,16 -19,-6" fill="#111"/>' \
         '<g stroke="#111" stroke-width="3"><line x1="0" y1="-20" x2="0" y2="-45"/><line x1="19" y1="-6" x2="43" y2="-14"/><line x1="12" y1="16" x2="26" y2="37"/><line x1="-12" y1="16" x2="-26" y2="37"/><line x1="-19" y1="-6" x2="-43" y2="-14"/></g></g>'
    return svg(d, b)


def leadership_forum():
    r = random.Random(8)
    d = lg("bg", [(0, "#10172b"), (1, "#27304f")]) + \
        '<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2c9" stop-opacity=".7"/><stop offset="1" stop-color="#fff2c9" stop-opacity="0"/></linearGradient>'
    b = f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'
    for x in (300, 600, 900):
        b += f'<polygon points="{x-14},0 {x+14},0 {x+190 if x>=600 else x+120},520 {x-190 if x<=600 else x-120},520" fill="url(#cone)"/>'
    b += '<ellipse cx="600" cy="520" rx="420" ry="60" fill="#d4af37" opacity=".35"/><ellipse cx="600" cy="505" rx="330" ry="40" fill="#d4af37" opacity=".5"/>'
    b += '<rect x="540" y="380" width="120" height="125" rx="6" fill="#d4af37"/><rect x="552" y="392" width="96" height="14" fill="#10172b" opacity=".35"/><circle cx="600" cy="334" r="26" fill="#0a0f1f"/><rect x="578" y="360" width="44" height="30" rx="14" fill="#0a0f1f"/>'
    for row, y in enumerate((590, 640)):
        for x in range(-20 + row * 30, W + 40, 62):
            b += f'<circle cx="{x}" cy="{y-26}" r="19" fill="#070b17"/><rect x="{x-24}" y="{y-8}" width="48" height="60" rx="22" fill="#070b17"/>'
    return svg(d, b)


def hero():
    r = random.Random(9)
    w, h = 1600, 560
    d = lg("bg", [(0, "#0a2f3d"), (.55, "#0e7c86"), (1, "#3b3fb8")], 1, 1)
    b = f'<rect width="{w}" height="{h}" fill="url(#bg)"/>'
    for _ in range(14):
        b += f'<circle cx="{r.randint(0,w)}" cy="{r.randint(0,h)}" r="{r.randint(30,170)}" fill="#fff" opacity="{r.uniform(.03,.08):.2f}"/>'
    for _ in range(46):  # confetti
        x, y = r.randint(0, w), r.randint(0, h)
        c = r.choice(["#ffd166", "#ef476f", "#06d6a0", "#fff", "#8ecae6"])
        b += f'<rect x="{x}" y="{y}" width="{r.randint(6,12)}" height="{r.randint(14,26)}" rx="2" fill="{c}" opacity=".75" transform="rotate({r.randint(0,180)} {x} {y})"/>'
    # ticket stub
    b += '<g transform="translate(1130 150) rotate(-10)"><path d="M0 0 H360 V92 a30 30 0 0 0 0 66 V250 H0 V158 a30 30 0 0 0 0 -66Z" fill="#fff" opacity=".95"/>' \
         '<line x1="250" y1="14" x2="250" y2="236" stroke="#0e7c86" stroke-width="3" stroke-dasharray="8 9"/>' \
         '<rect x="30" y="40" width="170" height="16" rx="8" fill="#0a2f3d"/><rect x="30" y="72" width="120" height="12" rx="6" fill="#0e7c86" opacity=".6"/>' \
         '<rect x="30" y="170" width="80" height="40" rx="8" fill="#ffd166"/>' \
         '<g fill="#0a2f3d">' + "".join(f'<rect x="{272+i*9}" y="{60+(i%3)*4}" width="{4+(i%2)*3}" height="{120-(i%4)*8}"/>' for i in range(9)) + '</g></g>'
    return svg(d, b, w, h)


FILES = {
    "sunset-beats.svg": sunset_beats, "tech-summit.svg": tech_summit, "city-marathon.svg": marathon,
    "founders-meetup.svg": founders_meetup, "acoustic-nights.svg": acoustic_nights, "ai-hackathon.svg": ai_hackathon,
    "football-cup.svg": football_cup, "leadership-forum.svg": leadership_forum, "hero.svg": hero,
}
if __name__ == "__main__":
    for name, fn in FILES.items():
        (OUT / name).write_text(fn(), encoding="utf-8")
        print("wrote", name)

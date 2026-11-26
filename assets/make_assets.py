#!/usr/bin/env python3
"""Generates the animated SVG assets for the profile README.

Run: python3 make_assets.py [output_dir]
Every asset uses CSS animations, which GitHub renders in images.
Themed assets come in -light and -dark versions for <picture> switching.
"""
import os, sys, math

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
os.makedirs(OUT, exist_ok=True)

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "light": dict(bg="#FFFFFF", card="#F6F8FA", border="#D0D7DE", text="#1F2328",
                  muted="#59636E", primary="#2C3E50", accent="#B7950B",
                  edge="#AFC0D2", soft="#E7EDF3", line="#D8DEE4",
                  err="#C93C37", warn="#B7791F", note="#3D6A9E"),
    "dark": dict(bg="#0D1117", card="#161B22", border="#30363D", text="#E6EDF3",
                 muted="#8B949E", primary="#9DB7D5", accent="#D4AC0D",
                 edge="#3A4A5E", soft="#1C2430", line="#2A323C",
                 err="#F0706A", warn="#E3A64A", note="#7FA7D9"),
}

def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", name)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------------------------------------------------------------- header
def header():
    W, H = 1000, 260
    # A small evolving graph on the right: nodes light up in turn,
    # a nod to node classification on evolving graphs.
    nodes = [(640,70),(720,40),(805,78),(890,48),(950,120),(870,140),(780,150),
             (700,130),(620,170),(690,210),(790,220),(880,205),(960,200),(560,110)]
    nodes = [(round(712 + (x - 560) * 0.62), y) for x, y in nodes]
    edges = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,2),(5,6),(6,7),(7,0),(7,8),(8,9),
             (9,10),(10,6),(10,11),(11,5),(11,12),(12,4),(0,13),(13,8),(2,6),(1,7)]
    e_svg = []
    for i,(a,b) in enumerate(edges):
        x1,y1 = nodes[a]; x2,y2 = nodes[b]
        e_svg.append(f'<line class="e" style="animation-delay:{(i%7)*0.4:.1f}s" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    n_svg = []
    for i,(x,y) in enumerate(nodes):
        d = (i*0.55) % 7.7
        n_svg.append(f'<circle class="halo" style="animation-delay:{d:.2f}s" cx="{x}" cy="{y}" r="11"/>'
                     f'<circle class="n" style="animation-delay:{d:.2f}s" cx="{x}" cy="{y}" r="5.5"/>')
    pulses = []
    for k,(a,b) in enumerate([(0,1),(5,6),(9,10),(13,8),(2,3),(11,12)]):
        x1,y1 = nodes[a]; x2,y2 = nodes[b]
        pulses.append(f'<circle r="2.6" fill="#F4D35E"><animateMotion dur="2.6s" begin="{k*0.7:.1f}s" repeatCount="indefinite" path="M{x1},{y1} L{x2},{y2}"/>'
                      f'<animate attributeName="opacity" values="0;1;1;0" dur="2.6s" begin="{k*0.7:.1f}s" repeatCount="indefinite"/></circle>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mahfuza Maisha. Problem-driven AI researcher, research mentor and full-stack developer.">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#16212E"/><stop offset="1" stop-color="#2C3E50"/>
  </linearGradient>
  <linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#16212E" stop-opacity="1"/><stop offset="0.68" stop-color="#16212E" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<style>
  text{{font-family:{FONT}}}
  .e{{stroke:#5D7690;stroke-width:1.2;stroke-dasharray:4 5;animation:flow 3s linear infinite}}
  .n{{fill:#7F95AD;animation:cls 7.7s ease-in-out infinite}}
  .halo{{fill:#D4AC0D;opacity:0;animation:halo 7.7s ease-in-out infinite}}
  .name{{font-size:48px;font-weight:700;fill:#FFFFFF;letter-spacing:.5px;opacity:0;animation:up .9s .1s cubic-bezier(.2,.7,.2,1) forwards}}
  .bar{{fill:#D4AC0D;transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow .8s .7s cubic-bezier(.2,.7,.2,1) forwards}}
  .sub{{font-size:19px;fill:#D5DEE8;opacity:0;animation:up .9s .9s cubic-bezier(.2,.7,.2,1) forwards}}
  .tag{{font:13px {MONO};fill:#AFC0D2;letter-spacing:.4px;opacity:0;animation:up .9s 1.3s cubic-bezier(.2,.7,.2,1) forwards}}
  @keyframes flow{{to{{stroke-dashoffset:-18}}}}
  @keyframes cls{{0%,40%,100%{{fill:#7F95AD}}50%,85%{{fill:#D4AC0D}}}}
  @keyframes halo{{0%,45%,100%{{opacity:0}}55%{{opacity:.28}}80%{{opacity:0}}}}
  @keyframes up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
  @keyframes grow{{to{{transform:scaleX(1)}}}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.name,.sub,.tag{{opacity:1}}.bar{{transform:none}}}}
</style>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g>{''.join(e_svg)}{''.join(n_svg)}{''.join(pulses)}</g>
  <rect width="{W}" height="{H}" fill="url(#fadeL)"/>
</g>
<text class="name" x="56" y="112">Mahfuza Maisha</text>
<rect class="bar" x="58" y="130" width="96" height="4" rx="2"/>
<text class="sub" x="56" y="170">Problem-driven AI researcher  |  Research mentor  |  Full-stack developer</text>
<text class="tag" x="57" y="206">NLP  \u00b7  graph learning  \u00b7  explainable ML  \u00b7  research tooling</text>
</svg>
'''

# ---------------------------------------------------------------- fields map
FIELDS = [
    ((170, 72),  "Fake news detection",  "NLP, knowledge graphs"),
    ((500, 46),  "Evolving graphs",      "social, citation, biology, finance"),
    ((830, 72),  "Air quality analysis", "bio-inspired rule mining"),
    ((862, 210), "Seismic inversion",    "physics-guided deep learning"),
    ((830, 348), "Research tooling",     "PaperPreflight"),
    ((500, 374), "Network simulation",   "TSN delay prediction"),
    ((170, 348), "Medical imaging",      "with mentored student teams"),
    ((138, 210), "Learning platforms",   "StudyDesk, teaching labs"),
]

def fields(t):
    T = THEMES[t]
    W, H, cx, cy = 1000, 420, 500, 210
    bw, bh = 232, 58
    edges, boxes, pulses = [], [], []
    for i, ((x, y), title, sub) in enumerate(FIELDS):
        d = 0.25 + i * 0.18
        L = math.hypot(x - cx, y - cy)
        edges.append(f'<path class="ed" style="stroke-dasharray:{L:.0f};stroke-dashoffset:{L:.0f};animation-delay:{d:.2f}s" d="M{cx},{cy} L{x},{y}"/>')
        boxes.append(f'''<g class="bx" style="animation-delay:{d+0.35:.2f}s">
  <rect x="{x-bw/2}" y="{y-bh/2}" width="{bw}" height="{bh}" rx="12" fill="{T['card']}" stroke="{T['border']}"/>
  <rect x="{x-bw/2}" y="{y-bh/2+14}" width="3" height="{bh-28}" rx="1.5" fill="{T['accent']}"/>
  <text x="{x}" y="{y-3}" text-anchor="middle" class="bt">{esc(title)}</text>
  <text x="{x}" y="{y+16}" text-anchor="middle" class="bs">{esc(sub)}</text>
</g>''')
        b = 2.2 + i * 0.45
        pulses.append(f'<circle r="3" fill="{T["accent"]}" opacity="0"><animateMotion dur="2.4s" begin="{b:.2f}s;p{i}.end+1.2s" id="p{i}" path="M{cx},{cy} L{x},{y}" keyPoints="0.25;0.8" keyTimes="0;1" calcMode="linear"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.8;1" dur="2.4s" begin="{b:.2f}s;p{i}.end+1.2s"/></circle>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Problems worked on: fake news detection, evolving graphs, air quality analysis, seismic inversion, research tooling, network simulation, medical imaging with mentored teams, and learning platforms.">
<style>
  text{{font-family:{FONT}}}
  .ed{{fill:none;stroke:{T['edge']};stroke-width:1.5;animation:draw 1s cubic-bezier(.4,0,.2,1) forwards}}
  .bx{{opacity:0;animation:pop .6s cubic-bezier(.2,.7,.2,1) forwards}}
  .bt{{font-size:15px;font-weight:600;fill:{T['text']}}}
  .bs{{font-size:12.5px;fill:{T['muted']}}}
  .core{{fill:{T['primary'] if t=='light' else '#22303F'}}}
  .ring{{fill:none;stroke:{T['accent']};stroke-width:2;stroke-dasharray:6 8;transform-origin:{cx}px {cy}px;animation:spin 18s linear infinite}}
  .ring2{{fill:none;stroke:{T['accent']};stroke-opacity:.35;stroke-width:1;transform-origin:{cx}px {cy}px;animation:breathe 3.2s ease-in-out infinite}}
  .ct{{font-size:15px;font-weight:600;fill:#FFFFFF}}
  .cs{{font-size:11px;fill:#D5DEE8;letter-spacing:.3px}}
  @keyframes draw{{to{{stroke-dashoffset:0}}}}
  @keyframes pop{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
  @keyframes spin{{to{{transform:rotate(360deg)}}}}
  @keyframes breathe{{0%,100%{{transform:scale(1);opacity:.35}}50%{{transform:scale(1.08);opacity:.9}}}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.bx{{opacity:1}}.ed{{stroke-dashoffset:0!important}}}}
</style>
{''.join(edges)}
{''.join(pulses)}
<circle class="ring2" cx="{cx}" cy="{cy}" r="92"/>
<circle class="ring" cx="{cx}" cy="{cy}" r="82"/>
<circle class="core" cx="{cx}" cy="{cy}" r="72"/>
<text class="ct" x="{cx}" y="{cy-4}" text-anchor="middle">Start from</text>
<text class="ct" x="{cx}" y="{cy+15}" text-anchor="middle">the problem</text>
<text class="cs" x="{cx}" y="{cy+34}" text-anchor="middle">then pick the method</text>
{''.join(boxes)}
</svg>
'''

# ---------------------------------------------------------------- stats strip
STATS = [("2", "IEEE conference papers"),
         ("15+", "student research teams mentored"),
         ("280+", "students taught over three terms"),
         ("Top 5%", "of the CSE batch, CGPA 3.73")]

def stats(t):
    T = THEMES[t]
    W, H = 1000, 128
    cw = W / len(STATS)
    cells = []
    for i, (big, lab) in enumerate(STATS):
        x = i * cw + cw / 2
        d = 0.15 + i * 0.22
        sep = f'<line x1="{i*cw:.0f}" y1="30" x2="{i*cw:.0f}" y2="98" stroke="{T["border"]}"/>' if i else ''
        cells.append(f'''{sep}<g class="c" style="animation-delay:{d:.2f}s">
  <text x="{x:.0f}" y="62" text-anchor="middle" class="big">{esc(big)}</text>
  <text x="{x:.0f}" y="88" text-anchor="middle" class="lab">{esc(lab)}</text>
</g>
<rect class="u" style="animation-delay:{d+0.4:.2f}s" x="{x-22:.0f}" y="100" width="44" height="3" rx="1.5"/>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="2 IEEE conference papers, 15+ student research teams mentored, 280+ students taught over three terms, top 5% of the CSE batch.">
<style>
  text{{font-family:{FONT}}}
  .big{{font-size:32px;font-weight:700;fill:{T['primary']}}}
  .lab{{font-size:13.5px;fill:{T['muted']}}}
  .c{{opacity:0;animation:up .7s cubic-bezier(.2,.7,.2,1) forwards}}
  .u{{fill:{T['accent']};transform-box:fill-box;transform-origin:center;transform:scaleX(0);animation:grow .6s cubic-bezier(.2,.7,.2,1) forwards}}
  @keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
  @keyframes grow{{to{{transform:scaleX(1)}}}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.c{{opacity:1}}.u{{transform:none}}}}
</style>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{T['card']}" stroke="{T['border']}"/>
{''.join(cells)}
</svg>
'''

# ---------------------------------------------------------------- PaperPreflight card
def preflight(t):
    T = THEMES[t]
    W, H = 1000, 300
    dx, dy, dw, dh = 612, 34, 250, 232      # document mock
    lines = []
    widths = [190, 205, 170, 210, 150, 198, 186, 120, 204, 176, 160]
    for i, w in enumerate(widths):
        y = dy + 40 + i * 16
        lines.append(f'<rect x="{dx+30}" y="{y}" width="{w}" height="6" rx="3" fill="{T["line"]}"/>'
                     f'<text x="{dx+12}" y="{y+6}" class="ln">{i+1}</text>')
    flags = [(2, T['err'], 1.6), (5, T['warn'], 2.4), (9, T['note'], 3.3)]
    fl = []
    for k, (row, col, at) in enumerate(flags):
        y = dy + 40 + row * 16
        fl.append(f'<g class="f{k}"><rect x="{dx+26}" y="{y-4}" width="{widths[row]+8}" height="14" rx="4" fill="{col}" fill-opacity=".16"/>'
                  f'<circle cx="{dx+dw-14}" cy="{y+3}" r="4.5" fill="{col}"/></g>')
    keyf = []
    for k, (_, _, at) in enumerate(flags):
        p = at / 9 * 100
        keyf.append(f'@keyframes f{k}{{0%,{p:.1f}%{{opacity:0}}{p+3:.1f}%,92%{{opacity:1}}97%,100%{{opacity:0}}}}'
                    f'.f{k}{{opacity:0;animation:f{k} 9s ease-out infinite}}')
    # score ring
    rx, ry, r = 925, 150, 44
    C = 2 * math.pi * r
    target = C * (1 - 0.71)
    chips = ["LaTeX, Word and PDF", "Runs in the browser", "Rule-based", "No API key"]
    chip_svg, x = [], 40
    for c in chips:
        w = 16 + len(c) * 7.3
        chip_svg.append(f'<rect x="{x}" y="214" width="{w:.0f}" height="28" rx="14" fill="{T["soft"]}" stroke="{T["border"]}"/>'
                        f'<text x="{x + w/2:.0f}" y="232.5" text-anchor="middle" class="chip">{esc(c)}</text>')
        x += w + 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="PaperPreflight: a private, rule-based pre-submission checker for research papers, scanning a manuscript, flagging three lines and showing a readiness score of 71.">
<style>
  text{{font-family:{FONT}}}
  .kick{{font:600 12px {MONO};letter-spacing:2px;fill:{T['accent']}}}
  .ttl{{font-size:36px;font-weight:700;fill:{T['text']}}}
  .d{{font-size:16px;fill:{T['muted']}}}
  .chip{{font-size:12.5px;font-weight:600;fill:{T['text']}}}
  .ln{{font:9px {MONO};fill:{T['muted']}}}
  .scan{{fill:{T['accent']};opacity:0;animation:scan 9s cubic-bezier(.4,0,.2,1) infinite}}
  .arc{{fill:none;stroke:{T['accent']};stroke-width:7;stroke-linecap:round;stroke-dasharray:{C:.1f};stroke-dashoffset:{C:.1f};transform:rotate(-90deg);transform-origin:{rx}px {ry}px;animation:arc 9s cubic-bezier(.2,.7,.2,1) infinite}}
  .score{{font-size:26px;font-weight:700;fill:{T['text']};opacity:0;animation:sc 9s ease-out infinite}}
  .sl{{font-size:11px;fill:{T['muted']};letter-spacing:.5px}}
  .in{{opacity:0;animation:in .8s cubic-bezier(.2,.7,.2,1) forwards}}
  @keyframes in{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
  @keyframes scan{{0%{{transform:translateY(0);opacity:0}}3%{{opacity:.9}}40%{{transform:translateY(180px);opacity:.9}}43%,100%{{transform:translateY(180px);opacity:0}}}}
  @keyframes arc{{0%,42%{{stroke-dashoffset:{C:.1f}}}58%,92%{{stroke-dashoffset:{target:.1f}}}100%{{stroke-dashoffset:{C:.1f}}}}}
  @keyframes sc{{0%,50%{{opacity:0}}58%,92%{{opacity:1}}100%{{opacity:0}}}}
  {''.join(keyf)}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.in,.score,.f0,.f1,.f2{{opacity:1}}.arc{{stroke-dashoffset:{target:.1f}}}}}
</style>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="{T['card']}" stroke="{T['border']}"/>
<g class="in" style="animation-delay:.1s"><text x="40" y="66" class="kick">RESEARCH TOOLING</text></g>
<g class="in" style="animation-delay:.3s"><text x="40" y="112" class="ttl">PaperPreflight</text></g>
<g class="in" style="animation-delay:.5s">
  <text x="40" y="150" class="d">A private, rule-based pre-submission checker for research</text>
  <text x="40" y="174" class="d">papers. It flags the slips reviewers notice first, line by line.</text>
</g>
<g class="in" style="animation-delay:.7s">{''.join(chip_svg)}</g>
<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="10" fill="{T['bg']}" stroke="{T['border']}"/>
<rect x="{dx}" y="{dy}" width="{dw}" height="24" rx="10" fill="{T['soft']}"/>
<rect x="{dx}" y="{dy+14}" width="{dw}" height="10" fill="{T['soft']}"/>
<text x="{dx+12}" y="{dy+16}" class="ln">paper.tex</text>
{''.join(lines)}
{''.join(fl)}
<rect class="scan" x="{dx+4}" y="{dy+34}" width="{dw-8}" height="2" rx="1"/>
<circle cx="{rx}" cy="{ry}" r="{r}" fill="none" stroke="{T['line']}" stroke-width="7"/>
<circle class="arc" cx="{rx}" cy="{ry}" r="{r}"/>
<text x="{rx}" y="{ry+9}" text-anchor="middle" class="score">71</text>
<text x="{rx}" y="{ry+68}" text-anchor="middle" class="sl">READINESS</text>
</svg>
'''


# ---------------------------------------------------------------- StudyDesk card
def studydesk(t):
    T = THEMES[t]
    W, H = 1000, 300
    # weekly schedule mock
    gx, gy, cw, rh = 560, 58, 46, 26
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    grid = []
    for i, d in enumerate(days):
        grid.append(f'<text x="{gx + i*cw + cw/2:.0f}" y="{gy-8}" text-anchor="middle" class="ln">{d}</text>')
    for r in range(6):
        grid.append(f'<line x1="{gx}" y1="{gy + r*rh}" x2="{gx + 5*cw}" y2="{gy + r*rh}" stroke="{T["line"]}"/>')
    blocks = [(0,0,2),(1,1,1),(2,0,1),(2,3,2),(3,2,2),(4,1,1),(0,3,1),(4,4,1),(1,3,1)]
    cols = [T['primary'], T['accent'], T['note']]
    for k, (d, r, n) in enumerate(blocks):
        grid.append(f'<rect class="blk" style="animation-delay:{0.6 + k*0.18:.2f}s" x="{gx + d*cw + 3}" y="{gy + r*rh + 3}" width="{cw-6}" height="{n*rh-6}" rx="5" fill="{cols[k%3]}" fill-opacity=".85"/>')
    # quiz mock
    qx, qy, qw = 830, 40, 140
    q = [f'<rect x="{qx}" y="{qy}" width="{qw}" height="168" rx="10" fill="{T["bg"]}" stroke="{T["border"]}"/>',
         f'<text x="{qx+12}" y="{qy+20}" class="qt">AI quiz from PDF</text>']
    for i in range(5):
        y = qy + 38 + i * 24
        q.append(f'<circle cx="{qx+18}" cy="{y}" r="6" fill="none" stroke="{T["border"]}"/>'
                 f'<circle class="qa q{i}" cx="{qx+18}" cy="{y}" r="6" fill="{T["accent"]}"/>'
                 f'<rect x="{qx+32}" y="{y-3}" width="{[86,70,92,64,80][i]}" height="6" rx="3" fill="{T["line"]}"/>')
    keyf = []
    for i in range(5):
        a = 20 + i * 8
        keyf.append(f'@keyframes q{i}{{0%,{a}%{{opacity:0}}{a+3}%,90%{{opacity:1}}96%,100%{{opacity:0}}}}.q{i}{{animation:q{i} 8s ease-out infinite}}')
    # goal bar
    bx, by, bw = 560, 236, 410
    goal = [f'<text x="{bx}" y="{by-8}" class="ln">Goal: finish chapter notes</text>',
            f'<rect x="{bx}" y="{by}" width="{bw}" height="8" rx="4" fill="{T["line"]}"/>',
            f'<rect class="gb" x="{bx}" y="{by}" width="{bw}" height="8" rx="4" fill="{T["accent"]}"/>']
    chips = ["Class schedule", "Study repository", "AI quizzes", "Goal tracking"]
    chip_svg, x = [], 40
    for c in chips:
        w = 16 + len(c) * 7.3
        chip_svg.append(f'<rect x="{x}" y="214" width="{w:.0f}" height="28" rx="14" fill="{T["soft"]}" stroke="{T["border"]}"/>'
                        f'<text x="{x + w/2:.0f}" y="232.5" text-anchor="middle" class="chip">{esc(c)}</text>')
        x += w + 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="StudyDesk: a Django study management platform with a weekly class schedule, a study repository, AI-generated quizzes from PDFs, and goal tracking.">
<style>
  text{{font-family:{FONT}}}
  .kick{{font:600 12px {MONO};letter-spacing:2px;fill:{T['accent']}}}
  .ttl{{font-size:36px;font-weight:700;fill:{T['text']}}}
  .d{{font-size:16px;fill:{T['muted']}}}
  .chip{{font-size:12.5px;font-weight:600;fill:{T['text']}}}
  .ln{{font:10px {MONO};fill:{T['muted']}}}
  .qt{{font-size:11.5px;font-weight:600;fill:{T['text']}}}
  .in{{opacity:0;animation:in .8s cubic-bezier(.2,.7,.2,1) forwards}}
  .blk{{opacity:0;transform-box:fill-box;transform-origin:center;animation:blk .5s cubic-bezier(.2,.7,.2,1) forwards}}
  .qa{{opacity:0}}
  .gb{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:gb 8s cubic-bezier(.4,0,.2,1) infinite}}
  @keyframes in{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
  @keyframes blk{{from{{opacity:0;transform:scale(.7)}}to{{opacity:1;transform:none}}}}
  @keyframes gb{{0%,10%{{transform:scaleX(0)}}70%,90%{{transform:scaleX(.8)}}100%{{transform:scaleX(0)}}}}
  {''.join(keyf)}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.in,.blk,.qa{{opacity:1}}.gb{{transform:scaleX(.8)}}}}
</style>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="{T['card']}" stroke="{T['border']}"/>
<g class="in" style="animation-delay:.1s"><text x="40" y="66" class="kick">STUDENT PRODUCTIVITY</text></g>
<g class="in" style="animation-delay:.3s"><text x="40" y="112" class="ttl">StudyDesk</text></g>
<g class="in" style="animation-delay:.5s">
  <text x="40" y="150" class="d">One place for a student's week: classes, notes, goals</text>
  <text x="40" y="174" class="d">and AI-generated quizzes from their own PDFs.</text>
</g>
<g class="in" style="animation-delay:.7s">{''.join(chip_svg)}</g>
{''.join(grid)}
{''.join(q)}
{''.join(goal)}
</svg>
'''

write("header.svg", header())
for t in THEMES:
    write(f"fields-{t}.svg", fields(t))
    write(f"stats-{t}.svg", stats(t))
    write(f"paperpreflight-{t}.svg", preflight(t))
    write(f"studydesk-{t}.svg", studydesk(t))

#!/usr/bin/env python3
"""Build a complete Custom DB asset set from a theme definition.

    python3 build_theme.py neon-grid assets/
    python3 build_theme.py --list

A theme is a palette plus a few style knobs. Every file lands at the exact
viewBox Custom DB (and DuelingBook) expects, so any theme drops in unchanged.
"""
import os, sys

# --------------------------------------------------------------------------
# Theme definitions.  p1 = you (bottom), p2 = opponent (top).
#   frame : bracket | double | dashed | cut | brush | block
#   glyph : diamond | cross | circle | pixel | none
#   bg    : city | rays | grid | flat | paper | scanlines
# --------------------------------------------------------------------------
THEMES = {
 'neon-grid': dict(
    label='Neon Grid', blurb='Synthwave skyline, corner brackets, hard neon.',
    ink='#05070d', panel='#0b1424', line='#22384f', text='#dceaf7',
    p1='#ff2d78', p2='#00e5ff', a1='#ffb020', a2='#39ff88',
    frame='bracket', glyph='diamond', lw=2.2, fill=0.34, bg='city'),
 'millennium': dict(
    label='Millennium', blurb='Carved sandstone and gold leaf. Sun-disc reticles, lapis and carnelian.',
    ink='#0d0a06', panel='#1a140c', line='#4a3a1c', text='#f2e4c4',
    p1='#c8452f', p2='#2f6bc8', a1='#e8b64c', a2='#3aa89b',
    frame='double', glyph='circle', lw=2.0, fill=0.30, bg='rays'),
 'blueprint': dict(
    label='Blueprint', blurb='Drafting table. Dashed zones, dimension ticks, annotation ink.',
    ink='#082340', panel='#0d3358', line='#2f6f9f', text='#e8f4ff',
    p1='#ff9a3c', p2='#7fe3ff', a1='#ffffff', a2='#b9e2ff',
    frame='dashed', glyph='cross', lw=1.6, fill=0.12, bg='grid'),
 'terminal': dict(
    label='Duel Terminal', blurb='Corroded industrial. Cut corners, hazard amber, patina and rust.',
    ink='#12100d', panel='#1d1a15', line='#3d3529', text='#e7e2d6',
    p1='#e2570c', p2='#4d9c73', a1='#eab308', a2='#a8a29e',
    frame='cut', glyph='none', lw=2.6, fill=0.35, bg='flat'),
 'sakura': dict(
    label='Sakura Dusk', blurb='Ink-wash twilight. Brushed borders, washi ground, gold seal.',
    ink='#171426', panel='#221d38', line='#4a4166', text='#f6ecf2',
    p1='#f0a6c8', p2='#7fb3d9', a1='#e8c98a', a2='#c9a227',
    frame='brush', glyph='circle', lw=3.0, fill=0.22, bg='paper'),
 'void': dict(
    label='Void', blurb='Pure black, hairline zones, one accent each side. Built for low-bitrate stream.',
    ink='#000000', panel='#0a0a0a', line='#242424', text='#ffffff',
    p1='#ff3b3b', p2='#3b8cff', a1='#ffffff', a2='#9a9a9a',
    frame='bracket', glyph='none', lw=1.5, fill=0.0, bg='flat'),
 'arcade': dict(
    label='Arcade CRT', blurb='Phosphor and scanlines. Blocky frames, pixel reticles, cabinet colours.',
    ink='#0b0f0b', panel='#111811', line='#264026', text='#ddffdd',
    p1='#ff5555', p2='#55ffff', a1='#ffee55', a2='#55ff55',
    frame='block', glyph='pixel', lw=4.0, fill=0.18, bg='scanlines'),
}

# ------------------------------- helpers ----------------------------------
def svg(w, h, body, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">{("<defs>"+defs+"</defs>") if defs else ""}{body}</svg>')

def glow_filter(fid, blur=3):
    return (f'<filter id="{fid}" x="-60%" y="-60%" width="220%" height="220%">'
            f'<feGaussianBlur stdDeviation="{blur}" result="b"/><feMerge>'
            f'<feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/>'
            f'</feMerge></filter>')

def frame_paths(T, x, y, w, h, c):
    """The zone outline, per the theme's frame style."""
    lw, o = T['lw'], 1.0
    if T['frame'] == 'bracket':
        a = min(15, w/4)
        d = (f'M{x},{y+a} L{x},{y} L{x+a},{y} M{x+w-a},{y} L{x+w},{y} L{x+w},{y+a} '
             f'M{x+w},{y+h-a} L{x+w},{y+h} L{x+w-a},{y+h} M{x+a},{y+h} L{x},{y+h} L{x},{y+h-a}')
        return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{lw}" stroke-linecap="square"/>'
    if T['frame'] == 'double':
        return (f'<rect x="{x+0.5}" y="{y+0.5}" width="{w-1}" height="{h-1}" fill="none" '
                f'stroke="{c}" stroke-width="{lw}"/>'
                f'<rect x="{x+5}" y="{y+5}" width="{w-10}" height="{h-10}" fill="none" '
                f'stroke="{c}" stroke-width="{lw*0.5}" stroke-opacity="0.55"/>')
    if T['frame'] == 'dashed':
        return (f'<rect x="{x+0.5}" y="{y+0.5}" width="{w-1}" height="{h-1}" fill="none" '
                f'stroke="{c}" stroke-width="{lw}" stroke-dasharray="7 5"/>'
                f'<path d="M{x+w/2},{y} v7 M{x+w/2},{y+h} v-7 M{x},{y+h/2} h7 M{x+w},{y+h/2} h-7" '
                f'stroke="{c}" stroke-width="{lw}" stroke-opacity="0.9"/>')
    if T['frame'] == 'cut':
        k = 12
        d = (f'M{x+k},{y} H{x+w-k} L{x+w},{y+k} V{y+h-k} L{x+w-k},{y+h} H{x+k} '
             f'L{x},{y+h-k} V{y+k} Z')
        return (f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{lw}" stroke-linejoin="miter"/>'
                f'<path d="M{x+k},{y} H{x+w-k}" stroke="{c}" stroke-width="{lw*1.8}" stroke-opacity="0.5"/>')
    if T['frame'] == 'brush':
        return ''.join(
            f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{lw}" stroke-linecap="round" '
            f'stroke-opacity="{op}"/>' for d, op in [
                (f'M{x+4},{y+2} Q{x+w/2},{y-1} {x+w-4},{y+3}', 0.95),
                (f'M{x+w-2},{y+5} Q{x+w+1},{y+h/2} {x+w-3},{y+h-5}', 0.8),
                (f'M{x+w-4},{y+h-2} Q{x+w/2},{y+h+1} {x+4},{y+h-3}', 0.95),
                (f'M{x+2},{y+h-5} Q{x-1},{y+h/2} {x+3},{y+5}', 0.8)])
    if T['frame'] == 'block':
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{c}" '
                f'stroke-width="{lw}"/>'
                f'<rect x="{x+lw*1.6}" y="{y+lw*1.6}" width="{w-lw*3.2}" height="{h-lw*3.2}" '
                f'fill="none" stroke="{c}" stroke-width="{lw*0.5}" stroke-opacity="0.4"/>')
    return ''

def glyph_mark(T, cx, cy, c):
    g = T['glyph']
    if g == 'diamond':
        r = 9
        return (f'<path d="M{cx},{cy-r} L{cx+r},{cy} L{cx},{cy+r} L{cx-r},{cy} Z" fill="none" '
                f'stroke="{c}" stroke-width="1.1" stroke-opacity="0.34"/>')
    if g == 'cross':
        return (f'<path d="M{cx-7},{cy} h14 M{cx},{cy-7} v14" stroke="{c}" stroke-width="1.2" '
                f'stroke-opacity="0.4" stroke-linecap="round"/>')
    if g == 'circle':
        return (f'<circle cx="{cx}" cy="{cy}" r="8" fill="none" stroke="{c}" stroke-width="1.2" '
                f'stroke-opacity="0.38"/><circle cx="{cx}" cy="{cy}" r="2.4" fill="{c}" '
                f'fill-opacity="0.45"/>')
    if g == 'pixel':
        return ''.join(f'<rect x="{cx+dx*4-2}" y="{cy+dy*4-2}" width="4" height="4" fill="{c}" '
                       f'fill-opacity="0.38"/>' for dx, dy in
                       [(0,-1),(-1,0),(1,0),(0,1)])
    return ''

def zone(T, x, y, w, h, c, kind='mon'):
    cx, cy = x + w/2, y + h/2
    parts = []
    if T['fill'] > 0:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{T["ink"]}" '
                     f'fill-opacity="{T["fill"]}"/>')
    parts.append(frame_paths(T, x, y, w, h, c))
    if kind == 'mon':
        parts.append(glyph_mark(T, cx, cy, c))
    elif kind == 'deck':
        parts.append(f'<path d="M{cx-9},{cy-13} h18 v22 h-18 Z M{cx-12},{cy-9} v22 h18" fill="none" '
                     f'stroke="{c}" stroke-width="1.1" stroke-opacity="0.32" stroke-linejoin="round"/>')
    return '<g>' + ''.join(parts) + '</g>'

# ------------------------------ backgrounds --------------------------------
def background(T):
    ink, p1, p2, a1 = T['ink'], T['p1'], T['p2'], T['a1']
    if T['bg'] == 'grid':
        b = (f'<defs><pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse">'
             f'<path d="M40,0 H0 V40" fill="none" stroke="{T["a2"]}" stroke-width="1" '
             f'stroke-opacity="0.16"/></pattern>'
             f'<pattern id="G" width="200" height="200" patternUnits="userSpaceOnUse">'
             f'<path d="M200,0 H0 V200" fill="none" stroke="{T["a1"]}" stroke-width="1.4" '
             f'stroke-opacity="0.22"/></pattern></defs>'
             f'<rect width="1920" height="1080" fill="{ink}"/>'
             f'<rect width="1920" height="1080" fill="url(#g)"/>'
             f'<rect width="1920" height="1080" fill="url(#G)"/>'
             f'<rect x="60" y="60" width="1800" height="960" fill="none" stroke="{T["a1"]}" '
             f'stroke-width="2" stroke-opacity="0.5"/>'
             f'<rect x="80" y="80" width="1760" height="920" fill="none" stroke="{T["a1"]}" '
             f'stroke-width="1" stroke-opacity="0.3"/>')
        return svg(1920, 1080, b)
    if T['bg'] == 'rays':
        rays = ''.join(
            f'<path d="M960,540 L{960+1500*__import__("math").cos(i*0.2618):.0f},'
            f'{540+1500*__import__("math").sin(i*0.2618):.0f} L'
            f'{960+1500*__import__("math").cos((i+0.5)*0.2618):.0f},'
            f'{540+1500*__import__("math").sin((i+0.5)*0.2618):.0f} Z" fill="{T["a1"]}" '
            f'fill-opacity="0.05"/>' for i in range(24))
        b = (f'<defs><radialGradient id="s"><stop offset="0" stop-color="{T["a1"]}" stop-opacity="0.5"/>'
             f'<stop offset="0.5" stop-color="{T["a1"]}" stop-opacity="0.12"/>'
             f'<stop offset="1" stop-color="{ink}" stop-opacity="0"/></radialGradient></defs>'
             f'<rect width="1920" height="1080" fill="{ink}"/>{rays}'
             f'<circle cx="960" cy="540" r="640" fill="url(#s)"/>'
             f'<circle cx="960" cy="540" r="300" fill="none" stroke="{T["a1"]}" stroke-width="3" '
             f'stroke-opacity="0.35"/>'
             f'<circle cx="960" cy="540" r="340" fill="none" stroke="{T["a1"]}" stroke-width="1.5" '
             f'stroke-opacity="0.22"/>')
        return svg(1920, 1080, b)
    if T['bg'] == 'paper':
        dots = ''.join(f'<circle cx="{(i*137)%1920}" cy="{(i*311)%1080}" r="{1+(i%3)}" '
                       f'fill="{T["a1"]}" fill-opacity="0.05"/>' for i in range(260))
        b = (f'<defs><linearGradient id="p" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{T["panel"]}"/><stop offset="1" stop-color="{ink}"/>'
             f'</linearGradient><radialGradient id="m" cx="0.72" cy="0.24" r="0.32">'
             f'<stop offset="0" stop-color="{T["a1"]}" stop-opacity="0.34"/>'
             f'<stop offset="1" stop-color="{T["a1"]}" stop-opacity="0"/></radialGradient></defs>'
             f'<rect width="1920" height="1080" fill="url(#p)"/>{dots}'
             f'<circle cx="1382" cy="259" r="150" fill="url(#m)"/>'
             f'<circle cx="1382" cy="259" r="92" fill="{T["a1"]}" fill-opacity="0.16"/>')
        return svg(1920, 1080, b)
    if T['bg'] == 'scanlines':
        lines = ''.join(f'<rect y="{y}" width="1920" height="2" fill="{T["a2"]}" '
                        f'fill-opacity="0.07"/>' for y in range(0, 1080, 4))
        b = (f'<defs><radialGradient id="v" cx="0.5" cy="0.5" r="0.75">'
             f'<stop offset="0" stop-color="{T["a2"]}" stop-opacity="0.13"/>'
             f'<stop offset="1" stop-color="{ink}" stop-opacity="0.9"/></radialGradient></defs>'
             f'<rect width="1920" height="1080" fill="{ink}"/>'
             f'<rect width="1920" height="1080" fill="url(#v)"/>{lines}')
        return svg(1920, 1080, b)
    if T['bg'] == 'city':
        return _city(T)
    # flat
    b = (f'<defs><radialGradient id="v" cx="0.5" cy="0.45" r="0.8">'
         f'<stop offset="0" stop-color="{T["panel"]}"/><stop offset="1" stop-color="{ink}"/>'
         f'</radialGradient></defs><rect width="1920" height="1080" fill="url(#v)"/>'
         f'<path d="M0,540 H1920" stroke="{T["a1"]}" stroke-width="1.5" stroke-opacity="0.18"/>')
    return svg(1920, 1080, b)

def _city(T):
    ink, p1, p2, a1 = T['ink'], T['p1'], T['p2'], T['a1']
    def towers(seed, y0, hmin, hmax, col, op, step):
        out, x, n = [], -40, 0
        while x < 1960:
            w = step * (0.55 + 0.4 * ((seed*(n+3)*37) % 11)/10)
            h = hmin + (hmax-hmin) * ((seed*(n+7)*53) % 17)/16
            out.append(f'<rect x="{x:.0f}" y="{y0-h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{col}"/>')
            if op > 0:
                for wy in range(int(y0-h)+14, int(y0)-10, 26):
                    for wx in range(int(x)+8, int(x+w)-8, 18):
                        if ((wx*7 + wy*13 + seed) % 5) < 2:
                            out.append(f'<rect x="{wx}" y="{wy}" width="5" height="9" '
                                       f'fill="{p2 if (wx+wy)%3 else p1}" fill-opacity="{op}"/>')
            x += w + step*0.12; n += 1
        return ''.join(out)
    b = (f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="#0a0418"/><stop offset="0.42" stop-color="#14103a"/>'
         f'<stop offset="0.68" stop-color="#2a1050"/><stop offset="1" stop-color="{ink}"/></linearGradient>'
         f'<radialGradient id="sun" cx="0.5" cy="0.62" r="0.34">'
         f'<stop offset="0" stop-color="{p1}" stop-opacity="0.85"/>'
         f'<stop offset="0.55" stop-color="#ff6a00" stop-opacity="0.32"/>'
         f'<stop offset="1" stop-color="#ff6a00" stop-opacity="0"/></radialGradient>'
         f'<linearGradient id="fog" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{ink}" stop-opacity="0"/>'
         f'<stop offset="1" stop-color="{ink}" stop-opacity="0.95"/></linearGradient>'
         f'<pattern id="grid" width="64" height="64" patternUnits="userSpaceOnUse">'
         f'<path d="M64,0 H0 V64" fill="none" stroke="{p2}" stroke-width="1" stroke-opacity="0.07"/>'
         f'</pattern></defs>'
         f'<rect width="1920" height="1080" fill="url(#sky)"/>'
         f'<rect width="1920" height="1080" fill="url(#grid)"/>'
         f'<circle cx="960" cy="670" r="330" fill="url(#sun)"/>'
         f'<g stroke="{ink}" stroke-width="12" opacity="0.55"><path d="M630,600 H1290 M630,650 H1290 '
         f'M630,700 H1290 M630,748 H1290"/></g>'
         f'<g opacity="0.85">{towers(3,800,90,300,"#0b0a24",0.0,96)}</g>'
         f'<g>{towers(7,900,120,430,"#07071a",0.55,128)}</g>'
         f'<g>{towers(11,1010,150,330,"#03040c",0.75,172)}</g>'
         f'<rect y="700" width="1920" height="380" fill="url(#fog)"/>')
    g = '<g opacity="0.5">'
    for i in range(-14, 15):
        g += f'<path d="M960,780 L{960+i*260},1080" stroke="{p2}" stroke-width="1" stroke-opacity="0.18"/>'
    yy, k = 782, 2.2
    while yy < 1090:
        g += f'<path d="M0,{yy:.0f} H1920" stroke="{p2}" stroke-width="1" stroke-opacity="0.16"/>'
        yy += k; k *= 1.42
    g += f'</g><path d="M0,780 H1920" stroke="{p1}" stroke-width="2" stroke-opacity="0.55"/>'
    return svg(1920, 1080, b + g)

# ------------------------------- the field ---------------------------------
COLS = [288, 381, 474, 567, 660]

def field_zones(T):
    p1, p2 = T['p1'], T['p2']
    parts = []
    for x in COLS:
        parts.append(zone(T, x, 60, 91, 91, p2, 'st'))
        parts.append(zone(T, x, 153, 91, 91, p2, 'mon'))
        parts.append(zone(T, x, 339, 91, 91, p1, 'mon'))
        parts.append(zone(T, x, 432, 91, 91, p1, 'st'))
    parts.append(zone(T, 381, 246, 91, 91, T['a1'], 'mon'))
    parts.append(zone(T, 567, 246, 91, 91, T['a1'], 'mon'))
    parts.append(zone(T, 221.5, 153, 64, 91, p2, 'st'))
    parts.append(zone(T, 753.5, 153, 64, 91, p2, 'st'))
    parts.append(zone(T, 221.5, 339, 64, 91, p1, 'st'))
    parts.append(zone(T, 753.5, 339, 64, 91, p1, 'st'))
    parts.append(zone(T, 207, 246, 64, 91, p2, 'mon'))
    parts.append(zone(T, 769, 246, 64, 91, p1, 'mon'))
    return svg(1024, 640, ''.join(parts))

def field_decks(T):
    p1, p2 = T['p1'], T['p2']
    return svg(1024, 640, ''.join([
        zone(T, 207, 28.5, 64, 91, p2, 'deck'), zone(T, 768, 28.5, 64, 91, p2, 'deck'),
        zone(T, 207, 463.5, 64, 91, p1, 'deck'), zone(T, 768, 463.5, 64, 91, p1, 'deck')]))

# ------------------------------- chrome ------------------------------------
def lamp(T, c, lit):
    of = 0.20 if not lit else 0.92
    orr = 0.45 if not lit else 1.0
    inner = (f'<circle cx="33" cy="33" r="15" fill="{c}" fill-opacity="{of}"/>'
             f'<circle cx="33" cy="33" r="15" fill="none" stroke="{c}" stroke-width="2.4" '
             f'stroke-opacity="{orr}"/>'
             f'<path d="M33,10 V18 M33,48 V56 M10,33 H18 M48,33 H56" stroke="{c}" stroke-width="3" '
             f'stroke-linecap="round" stroke-opacity="{orr}"/>'
             f'<circle cx="33" cy="33" r="24" fill="none" stroke="{c}" stroke-width="1.2" '
             f'stroke-opacity="{0.25 if not lit else 0.6}" stroke-dasharray="4 7"/>')
    if lit:
        return svg(66, 66, f'<g filter="url(#g)">{inner}</g>', glow_filter('g', 3.4))
    return svg(66, 66, inner)

def turn_bar(T, c):
    return svg(80, 30, f'<g filter="url(#g)">'
        f'<path d="M9,3 H71 L77,9 V21 L71,27 H9 L3,21 V9 Z" fill="{c}" fill-opacity="0.22"/>'
        f'<path d="M9,3 H71 L77,9 V21 L71,27 H9 L3,21 V9 Z" fill="none" stroke="{c}" stroke-width="2.2"/>'
        f'<path d="M14,15 H66" stroke="{c}" stroke-width="2.4" stroke-opacity="0.8" '
        f'stroke-linecap="round" stroke-dasharray="3 6"/></g>', glow_filter('g', 2.6))

def button_bg(T):
    return svg(111, 111,
        f'<path d="M20,6 H91 L105,20 V91 L91,105 H20 L6,91 V20 Z" fill="{T["panel"]}" fill-opacity="0.92"/>'
        f'<path d="M20,6 H91 L105,20 V91 L91,105 H20 L6,91 V20 Z" fill="none" stroke="{T["line"]}" '
        f'stroke-width="1.5"/>'
        f'<path d="M20,6 H44 M67,6 H91 M105,20 V44 M105,67 V91 M91,105 H67 M44,105 H20 M6,91 V67 M6,44 V20" '
        f'fill="none" stroke="{T["p2"]}" stroke-width="2" stroke-opacity="0.55" stroke-linecap="round"/>'
        f'<circle cx="55.5" cy="55.5" r="40" fill="none" stroke="{T["line"]}" stroke-width="1"/>'
        f'<circle cx="55.5" cy="55.5" r="33" fill="{T["ink"]}" fill-opacity="0.6"/>')

def counter(T, lit):
    c, o = T['a1'], (1.0 if lit else 0.7)
    inner = (f'<path d="M19,2 L35,11 V30 L19,39 L3,30 V11 Z" fill="{T["ink"]}" fill-opacity="0.96"/>'
             f'<path d="M19,2 L35,11 V30 L19,39 L3,30 V11 Z" fill="none" stroke="{c}" '
             f'stroke-width="2.2" stroke-opacity="{o}"/>'
             f'<path d="M19,9 L29,14.8 V26.4 L19,32.2 L9,26.4 V14.8 Z" fill="{c}" '
             f'fill-opacity="{0.35 if lit else 0.14}"/>')
    if lit:
        return svg(38.08, 40.64, f'<g filter="url(#g)">{inner}</g>', glow_filter('g', 2.2))
    return svg(38.08, 40.64, inner)

# ------------------------------- emit --------------------------------------
def build(name, outdir):
    T = THEMES[name]
    os.makedirs(outdir, exist_ok=True)
    W = lambda f, s: open(os.path.join(outdir, f), 'w').write(s)
    W('background.svg', background(T))
    W('field_zones2.svg', field_zones(T))
    W('field_decks2.svg', field_decks(T))
    W('button_bg.svg', button_bg(T))
    W('button_blue.svg', lamp(T, T['p2'], False)); W('button_blue_lit.svg', lamp(T, T['p2'], True))
    W('button_red.svg',  lamp(T, T['p1'], False)); W('button_red_lit.svg',  lamp(T, T['p1'], True))
    W('turn_red.svg', turn_bar(T, T['p1'])); W('turn_blue.svg', turn_bar(T, T['p2']))
    W('turn_yellow.svg', turn_bar(T, T['a1'])); W('turn_green.svg', turn_bar(T, T['a2']))
    W('counter.svg', counter(T, False)); W('counter_glow.svg', counter(T, True))
    return len(os.listdir(outdir))

if __name__ == '__main__':
    if '--list' in sys.argv or len(sys.argv) < 3:
        for k, v in THEMES.items():
            print(f'  {k:<12} {v["label"]:<16} {v["blurb"]}')
        sys.exit(0 if '--list' in sys.argv else 1)
    n = build(sys.argv[1], sys.argv[2])
    print(f'{sys.argv[1]} -> {sys.argv[2]}  ({n} files)')

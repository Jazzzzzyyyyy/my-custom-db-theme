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
def turn_background(T):
    return svg(301, 111,
        f'<path d="M18,6 H283 L295,18 V93 L283,105 H18 L6,93 V18 Z" fill="{T["panel"]}" fill-opacity="0.94"/>'
        f'<path d="M18,6 H283 L295,18 V93 L283,105 H18 L6,93 V18 Z" fill="none" stroke="{T["line"]}" stroke-width="1.5"/>'
        f'<path d="M18,6 H60 M241,6 H283 M295,18 V40 M295,71 V93 M283,105 H241 M60,105 H18 M6,93 V71 M6,40 V18" '
        f'fill="none" stroke="{T["p2"]}" stroke-width="2" stroke-opacity="0.5" stroke-linecap="round"/>'
        f'<rect x="24" y="24" width="253" height="63" rx="4" fill="{T["ink"]}" fill-opacity="0.55"/>'
        f'<path d="M24,24 H70 M231,87 H277" stroke="{T["p1"]}" stroke-width="2" stroke-opacity="0.6" stroke-linecap="round"/>')

def white_glow(T):
    return svg(116.2, 82.49,
        '<ellipse cx="58.1" cy="41.2" rx="58.1" ry="41.2" fill="url(#wg)"/>',
        f'<radialGradient id="wg"><stop offset="0" stop-color="#ffffff" stop-opacity="0.85"/>'
        f'<stop offset="0.45" stop-color="{T["p2"]}" stop-opacity="0.35"/>'
        f'<stop offset="1" stop-color="{T["p2"]}" stop-opacity="0"/></radialGradient>')

def profile(T, c):
    return svg(376, 320,
        f'<path d="M30,2 H346 L374,30 V290 L346,318 H30 L2,290 V30 Z" fill="{T["panel"]}" fill-opacity="0.9"/>'
        f'<path d="M30,2 H346 L374,30 V290 L346,318 H30 L2,290 V30 Z" fill="none" stroke="{c}" stroke-width="2.5" stroke-opacity="0.55"/>'
        f'<path d="M30,2 H96 M280,2 H346 M374,30 V96 M374,224 V290 M346,318 H280 M96,318 H30 M2,290 V224 M2,96 V30" '
        f'fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round"/>'
        f'<path d="M2,30 L30,2 M374,290 L346,318" stroke="{c}" stroke-width="4" stroke-linecap="round"/>'
        f'<rect x="14" y="14" width="348" height="292" rx="4" fill="none" stroke="{c}" stroke-width="1" stroke-opacity="0.22"/>'
        f'<path d="M12,160 H2 M374,160 H364" stroke="{c}" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M150,308 H226" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-opacity="0.5"/>')

def cell(T, selected):
    if not selected:
        return svg(200, 20,
            f'<rect width="200" height="20" fill="{T["panel"]}"/>'
            f'<rect width="200" height="20" fill="none" stroke="{T["line"]}" stroke-width="1"/>'
            f'<rect width="2.5" height="20" fill="{T["p2"]}" fill-opacity="0.35"/>')
    return svg(200, 20,
        f'<rect width="200" height="20" fill="{T["panel"]}"/><rect width="200" height="20" fill="url(#s)"/>'
        f'<rect width="3" height="20" fill="{T["p2"]}"/>'
        f'<rect x="0.5" y="0.5" width="199" height="19" fill="none" stroke="{T["p2"]}" stroke-width="1" stroke-opacity="0.55"/>',
        f'<linearGradient id="s" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{T["p2"]}" stop-opacity="0.30"/>'
        f'<stop offset="1" stop-color="{T["p1"]}" stop-opacity="0.12"/></linearGradient>')

def laser_sword(T):
    art = ('<g filter="url(#g)">'
        '<rect x="18" y="19" width="6" height="15" rx="2" fill="#7f8fa6"/>'
        '<rect x="26" y="14" width="5" height="25" rx="2" fill="#aab6c6"/>'
        '<path d="M33,26.5 L176,18 L196,26.5 L176,35 Z" fill="url(#blade)"/>'
        '<path d="M33,26.5 H190" stroke="#ffffff" stroke-width="2" stroke-opacity="0.9" stroke-linecap="round"/>'
        '<path d="M40,26.5 H120" stroke="#ffffff" stroke-width="5" stroke-opacity="0.35" stroke-linecap="round"/></g>')
    return svg(200, 53, art, glow_filter('g', 3) +
        f'<linearGradient id="blade" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{T["p1"]}"/><stop offset="0.55" stop-color="{T["p2"]}"/>'
        f'<stop offset="1" stop-color="#ffffff"/></linearGradient>')

def _slot(T, x, y, w, h, c, op=0.5, arm=7):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{T["ink"]}" fill-opacity="0.5"/>'
            f'<rect x="{x+0.5}" y="{y+0.5}" width="{w-1}" height="{h-1}" fill="none" stroke="{c}" '
            f'stroke-width="1" stroke-opacity="{op*0.4}"/>'
            f'<path d="M{x},{y+arm} V{y} H{x+arm} M{x+w-arm},{y} H{x+w} V{y+arm} M{x+w},{y+h-arm} V{y+h} '
            f'H{x+w-arm} M{x+arm},{y+h} H{x} V{y+h-arm}" fill="none" stroke="{c}" stroke-width="1.6" '
            f'stroke-opacity="{op}"/>')

def deck_constructor(T):
    P, L, p2, a1 = T['panel'], T['line'], T['p2'], T['a1']
    b = [f'<path d="M216,4 H794 V470 H216 Q206,470 206,460 V14 Q206,4 216,4 Z" fill="{P}" fill-opacity="0.97"/>',
         f'<path d="M216,4 H794 V470 H216 Q206,470 206,460 V14 Q206,4 216,4 Z" fill="none" stroke="{L}" stroke-width="1.5"/>',
         f'<path d="M206,60 V150 M206,320 V410" stroke="{p2}" stroke-width="2.5" stroke-opacity="0.7" stroke-linecap="round"/>']
    for r in range(6):
        for c_ in range(10):
            b.append(_slot(T, 244 + 55*c_, 5 + 77.5*r, 54, 76.5, p2, 0.4))
    b.append(f'<path d="M221,474 H794 V552.5 H221 Q216,552.5 216,547.5 V479 Q216,474 221,474 Z" fill="{P}" fill-opacity="0.97"/>')
    b.append(f'<path d="M216,479 V547.5" stroke="{p2}" stroke-width="3" stroke-linecap="round"/>')
    b.append(f'<path d="M221,556.5 H794 V635 H221 Q216,635 216,630 V561.5 Q216,556.5 221,556.5 Z" fill="{P}" fill-opacity="0.97"/>')
    b.append(f'<path d="M216,561.5 V630" stroke="{a1}" stroke-width="3" stroke-linecap="round"/>')
    for i in range(15):
        x = 244 + 36.643*i
        b.append(_slot(T, x, 487.75, 36, 51, p2, 0.5, 6))
        b.append(_slot(T, x, 570.25, 36, 51, a1, 0.5, 6))
    return svg(1024, 640, ''.join(b))

def search_panel(T):
    P, L, p2 = T['panel'], T['line'], T['p2']
    s = [f'<path d="M12,0 H221 V630.5 H0 V12 Q0,0 12,0 Z" fill="{P}" fill-opacity="0.97"/>',
         f'<path d="M12,0 H221 M0,12 V630.5" fill="none" stroke="{L}" stroke-width="1.5"/>',
         f'<path d="M0,40 V120 M0,300 V380" stroke="{p2}" stroke-width="2.5" stroke-opacity="0.7" stroke-linecap="round"/>',
         f'<path d="M14,236 H207" stroke="{p2}" stroke-width="1" stroke-opacity="0.3"/>']
    for r in range(5):
        for c_ in range(4):
            s.append(_slot(T, 1 + 55*c_, 243.5 + 77.5*r, 54, 76.5, p2, 0.4))
    return svg(221, 630.5, ''.join(s))

ICON_ART = {
 'die_btn': ('<path d="M50,8 L88,29 V71 L50,92 L12,71 V29 Z" fill="{C}" fill-opacity="{F}"/>'
   '<path d="M50,8 L88,29 V71 L50,92 L12,71 V29 Z" fill="none" stroke="{C}" stroke-width="{SW}" stroke-linejoin="round"/>'
   '<path d="M50,8 V50 M50,50 L88,29 M50,50 L12,29" fill="none" stroke="{C}" stroke-width="{SWt}" stroke-opacity="0.55"/>'
   '<circle cx="50" cy="28" r="5" fill="{C}"/><circle cx="68" cy="60" r="5" fill="{C}"/><circle cx="32" cy="60" r="5" fill="{C}"/>'),
 'coin_btn': ('<circle cx="50" cy="50" r="38" fill="{C}" fill-opacity="{F}"/>'
   '<circle cx="50" cy="50" r="38" fill="none" stroke="{C}" stroke-width="{SW}"/>'
   '<circle cx="50" cy="50" r="27" fill="none" stroke="{C}" stroke-width="{SWt}" stroke-opacity="0.6"/>'
   '<path d="M50,30 V70 M38,38 H62 M38,62 H62" stroke="{C}" stroke-width="{SW}" stroke-linecap="round"/>'),
 'token_btn': ('<path d="M50,10 L84,30 V70 L50,90 L16,70 V30 Z" fill="{C}" fill-opacity="{F}"/>'
   '<path d="M50,10 L84,30 V70 L50,90 L16,70 V30 Z" fill="none" stroke="{C}" stroke-width="{SW}" stroke-linejoin="round"/>'
   '<path d="M50,26 L70,38 V62 L50,74 L30,62 V38 Z" fill="none" stroke="{C}" stroke-width="{SWt}" stroke-opacity="0.7" stroke-linejoin="round"/>'),
 'sort_btn': ('<path d="M20,22 H80 M20,40 H64 M20,58 H48 M20,76 H34" stroke="{C}" stroke-width="{SW}" stroke-linecap="round"/>'
   '<path d="M78,52 V84 M68,74 L78,84 L88,74" fill="none" stroke="{C}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"/>'),
 'info_btn': ('<path d="M24,32 H68 M58,22 L70,32 L58,42" fill="none" stroke="{C}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"/>'
   '<path d="M76,68 H32 M42,58 L30,68 L42,78" fill="none" stroke="{C}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"/>'),
 'search_prev_btn': ('<circle cx="50" cy="50" r="40" fill="{C}" fill-opacity="{F}"/>'
   '<circle cx="50" cy="50" r="40" fill="none" stroke="{C}" stroke-width="{SW}"/>'
   '<path d="M58,30 L38,50 L58,70" fill="none" stroke="{C}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"/>'),
 'search_next_btn': ('<circle cx="50" cy="50" r="40" fill="{C}" fill-opacity="{F}"/>'
   '<circle cx="50" cy="50" r="40" fill="none" stroke="{C}" stroke-width="{SW}"/>'
   '<path d="M42,30 L62,50 L42,70" fill="none" stroke="{C}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"/>'),
}
ICON_SIZE = {'die_btn': (409.69, 485.99), 'coin_btn': (75.6, 66.76), 'token_btn': (38.59, 36.51),
             'sort_btn': (55.8, 55.82), 'info_btn': (25.01, 25.01),
             'search_prev_btn': (29.95, 30), 'search_next_btn': (30, 30)}

def icon(T, name, state):
    w, h = ICON_SIZE[name]
    c, f, sw, swt, gl = {
        'up':   (T['p2'], 0.10, 6, 3, False),
        'over': (T['p2'], 0.22, 7, 3.5, True),
        'down': (T['p1'], 0.38, 7, 3.5, True),
    }[state]
    k = min(w, h) / 100.0
    tx, ty = (w - 100*k)/2, (h - 100*k)/2
    inner = ICON_ART[name].format(C=c, F=f, SW=sw, SWt=swt)
    defs = ''
    if gl:
        defs = glow_filter('g', 3)
        inner = f'<g filter="url(#g)">{inner}</g>'
    return svg(w, h, f'<g transform="translate({tx:.2f},{ty:.2f}) scale({k:.5f})">{inner}</g>', defs)


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
    W('turn_background.svg', turn_background(T))
    W('turn_red.svg', turn_bar(T, T['p1'])); W('turn_blue.svg', turn_bar(T, T['p2']))
    W('turn_yellow.svg', turn_bar(T, T['a1'])); W('turn_green.svg', turn_bar(T, T['a2']))
    W('white_glow.svg', white_glow(T))
    W('counter.svg', counter(T, False)); W('counter_glow.svg', counter(T, True))
    W('profile_bg_red.svg', profile(T, T['p1'])); W('profile_bg_blue.svg', profile(T, T['p2']))
    W('cell4.svg', cell(T, False)); W('cell_sel.svg', cell(T, True))
    W('check.svg', svg(14, 14, f'<path d="M2,7.4 L5.4,11 L12,3" fill="none" stroke="{T["a2"]}" '
                                f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'))
    W('radio.svg', svg(14, 14, f'<circle cx="7" cy="7" r="3.6" fill="{T["p2"]}"/>'
                                f'<circle cx="7" cy="7" r="6" fill="none" stroke="{T["p2"]}" '
                                f'stroke-width="1" stroke-opacity="0.45"/>'))
    W('combobox_arrow.svg', svg(24, 12, f'<path d="M4,3.5 L12,9.5 L20,3.5" fill="none" '
                                        f'stroke="{T["p2"]}" stroke-width="2.4" stroke-linecap="round" '
                                        f'stroke-linejoin="round"/>'))
    W('laser_sword.svg', laser_sword(T))
    W('deck_constructor.svg', deck_constructor(T))
    W('search.svg', search_panel(T))
    for n in ICON_ART:
        for st in ('up', 'over', 'down'):
            W(f'{n}_{st}.svg', icon(T, n, st))
    return len(os.listdir(outdir))


def _lighten(hexcolor, amt=0.45):
    """Mix a colour toward white; used for counter digits, which sit on dark art."""
    h = hexcolor.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    f = lambda v: int(v + (255 - v) * amt)
    return '#%02x%02x%02x' % (f(r), f(g), f(b))


def theme_palette(name):
    """The palette the userscript's CSS layer needs, as a JSON-ready dict."""
    T = THEMES[name]
    p = {k: T[k] for k in ('ink', 'panel', 'line', 'text', 'p1', 'p2', 'a1', 'a2')}
    p['a1soft'] = T.get('a1soft', _lighten(T['a1']))
    return p


if __name__ == '__main__':
    if '--list' in sys.argv or len(sys.argv) < 3:
        for k, v in THEMES.items():
            print(f'  {k:<12} {v["label"]:<16} {v["blurb"]}')
        sys.exit(0 if '--list' in sys.argv else 1)
    n = build(sys.argv[1], sys.argv[2])
    print(f'{sys.argv[1]} -> {sys.argv[2]}  ({n} files)')

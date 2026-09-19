#!/usr/bin/env python3
"""Generate every theme as a self-contained, installable userscript.

    python3 build_all.py

Writes themes/<key>/assets/*.svg (47 files) and themes/<key>/custom-duelingbook.user.js
for each theme in build_theme.THEMES. Each script is independent: its own name in
Tampermonkey, its own settings storage, its own asset URLs and CSS palette.

Only ever enable ONE at a time — they all match duelingbook.com and would
otherwise fight over the same DOM nodes.
"""
import json, os, re, shutil, sys
from build_theme import THEMES, build, theme_palette

OWNER, REPO, BRANCH = 'Jazzzzzyyyyy', 'my-custom-db-theme', 'main'
RAW = f'https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}'
ROOT = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(ROOT, 'custom-duelingbook.user.js')
BASE_RE = re.compile(re.escape(RAW) + r'/assets')


def make_script(key, master):
    T = THEMES[key]
    s = master
    # 1. asset base -> this theme's folder
    s = BASE_RE.sub(f'{RAW}/themes/{key}/assets', s)
    # 2. CSS palette
    pal = json.dumps(theme_palette(key), separators=(',', ':'))
    s, n = re.subn(r'const NEON_THEME = \{.*?\};', f'const NEON_THEME = {pal};', s, count=1)
    if n != 1:
        raise SystemExit('could not find the NEON_THEME line in the master script')
    # 3. identity — distinct name and namespace so Tampermonkey lists them separately
    s = s.replace('// @name         Custom DB — Neon Grid',
                  f'// @name         Custom DB — {T["label"]}', 1)
    s = s.replace('// @description  Custom DB with the Neon Grid cyberpunk asset pack baked in',
                  f'// @description  Custom DB themed with the {T["label"]} asset pack — {T["blurb"]}', 1)
    s = re.sub(r'// @namespace    \S+', f'// @namespace    https://github.com/{OWNER}/{REPO}#{key}', s, count=1)
    for tag in ('updateURL', 'downloadURL'):
        s = re.sub(rf'// @{tag}\s+\S+',
                   f'// @{tag}  {RAW}/themes/{key}/custom-duelingbook.user.js', s, count=1)
    return s


def main():
    master = open(MASTER).read()
    if 'const NEON_THEME' not in master:
        raise SystemExit('master script is missing the NEON_THEME palette line')
    out = os.path.join(ROOT, 'themes')
    shutil.rmtree(out, ignore_errors=True)
    for key in THEMES:
        d = os.path.join(out, key)
        n = build(key, os.path.join(d, 'assets'))
        open(os.path.join(d, 'custom-duelingbook.user.js'), 'w').write(make_script(key, master))
        print(f'  {key:<12} {n} assets + userscript')
    print(f'{len(THEMES)} themes -> themes/')


if __name__ == '__main__':
    main()

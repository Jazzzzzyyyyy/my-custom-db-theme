#!/usr/bin/env python3
"""Emit a Custom DB settings file that points every themeable asset at your host.

    python3 make-settings.py https://raw.githubusercontent.com/<you>/<repo>/main/assets
    -> writes custom-db-settings.json, then Import it from the Custom DB gear.
"""
import json, sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
BASE = sys.argv[1].rstrip('/')
u = lambda f: f'{BASE}/{f}'

cfg = {
    # --- field ---
    'deckZoneImageUrl':  u('field_decks2.svg'),
    'fieldZoneImageUrl': u('field_zones2.svg'),
    # MR3 has a different zone layout (no Extra Monster / Pendulum zones), so the
    # Neon Grid field art would sit in the wrong places — leave DuelingBook's own.
    'deckZoneImageUrlMr3':  'https://images.duelingbook.com/svg/field_decks.svg',
    'fieldZoneImageUrlMr3': 'https://images.duelingbook.com/svg/field_zones.svg',
    'backgroundUrl':        u('background.svg'),
    'attackSwordImageUrl':  u('laser_sword.svg'),
    # --- phase + turn ---
    'phaseButtonBackgroundImageUrl': u('button_bg.svg'),
    'phaseButtonRedImageUrl':        u('button_red.svg'),
    'phaseButtonRedActiveImageUrl':  u('button_red_lit.svg'),
    'phaseButtonBlueImageUrl':       u('button_blue.svg'),
    'phaseButtonBlueActiveImageUrl': u('button_blue_lit.svg'),
    'turnButtonBackgroundImageUrl':  u('turn_background.svg'),
    'turnButtonRedImageUrl':         u('turn_red.svg'),
    'turnButtonBlueImageUrl':        u('turn_blue.svg'),
    'turnButtonYellowImageUrl':      u('turn_yellow.svg'),
    'turnButtonGreenImageUrl':       u('turn_green.svg'),
    'turnButtonGlowImageUrl':        u('white_glow.svg'),
    'counterButtonImageUrl':         u('counter.svg'),
    'counterButtonGlowImageUrl':     u('counter_glow.svg'),
    # --- profiles + panels ---
    'profileRedBorderImageUrl':       u('profile_bg_red.svg'),
    'profileBlueBorderImageUrl':      u('profile_bg_blue.svg'),
    'deckConstructorBackgroundImage': u('deck_constructor.svg'),
    'deckConstructorSearchImage':     u('search.svg'),
    # --- companion switches the skin assumes ---
    'darkMode': True,
    'darkModeLog': True,
    'hideBackgroundBox': True,
    'hideFieldSpellBackground': True,
    'deckConstructorSearchLightFontColor': True,
}

# --- three-state buttons: identifier in the script -> our file stem ---
BUTTONS = {
    'd_die_btn': 'die_btn',
    'd_coin_btn': 'coin_btn',
    'd_token_btn': 'token_btn',
    'dc_token_btn': 'token_btn',
    'dc_sort_btn': 'sort_btn',
    'dc_info_btn': 'info_btn',
    'dc_search_prev_btn': 'search_prev_btn',
    'dc_search_next_btn': 'search_next_btn',
}
for ident, stem in BUTTONS.items():
    for state in ('up', 'over', 'down'):
        cfg[f'{ident}_{state}'] = u(f'{stem}_{state}.svg')

with open('custom-db-settings.json', 'w') as fh:
    json.dump(cfg, fh, indent=2)
print(f'custom-db-settings.json written — {len(cfg)} keys, base {BASE}')

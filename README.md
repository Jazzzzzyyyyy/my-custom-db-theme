# Neon Grid — a cyberpunk theme for DuelingBook

47 SVGs that replace DuelingBook's default art, plus a copy of the
[Custom DB](https://github.com/killburne/custom-duelingbook/) userscript with every
asset URL already pointed at this repo. Each file keeps the original asset's exact
`viewBox`, so nothing needs CSS changes.

## Install

1. **Install the script.** Open
   [`custom-duelingbook.user.js`](https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/custom-duelingbook.user.js)
   with Tampermonkey installed — it offers to install. If you already run the stock
   Custom DB, **disable it first**; running both at once will fight over the DOM.
2. **Reset to the new defaults.** Open duelingbook.com, click the gear at the
   bottom-left, and hit *Reset to defaults* — otherwise Tampermonkey keeps the URLs
   you had saved and the theme won't show.
3. Recommended switches, all in the same panel:
   Dark Mode **on** · Dark Mode Log **on** · Hide Background Box **on** ·
   Hide Field Spell Background **on** · Light Font Color For Search Labels **on**.

### Keeping the stock script instead

If you'd rather not swap scripts, keep the official Custom DB and just import the URLs:

```
python3 make-settings.py https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/assets
```

Then gear → **Import Settings** → pick `custom-db-settings.json` → Save.

## Palette

| Role | Hex | Used for |
|---|---|---|
| Void | `#05070D` | page ground |
| Panel | `#0B1424` | bars, cards, constructor |
| Cyan | `#00E5FF` | player 2, all neutral UI |
| Magenta | `#FF2D78` | player 1, pressed states |
| Amber | `#FFB020` | counters, side deck rail |
| Acid | `#39FF88` | checkmarks, ready state |

Type: **Chakra Petch** (display) over **IBM Plex Mono** (numbers, logs).

## Other themes

Seven themes are generated as **independent userscripts** under `themes/`. Each has
its own name in Tampermonkey, its own settings storage, its own 47 assets and its
own CSS palette — so you can install several and flip between them.

> **Enable only one at a time.** They all match `duelingbook.com`; two enabled at
> once will fight over the same DOM nodes. Toggling in the Tampermonkey dashboard
> takes a second and each script keeps its own settings.

| Theme | Look | Install |
|---|---|---|
| `neon-grid` | Synthwave skyline, corner brackets, hard neon | [install](https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/themes/neon-grid/custom-duelingbook.user.js) |
| `millennium` | Carved sandstone and gold leaf, sun-disc reticles, lapis and carnelian | [install](https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/themes/millennium/custom-duelingbook.user.js) |
| `blueprint` | Drafting table — dashed zones, dimension ticks, annotation ink | [install](https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/themes/blueprint/custom-duelingbook.user.js) |
| `terminal` | Corroded industrial — cut corners, hazard amber, patina and rust | [install](https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/themes/terminal/custom-duelingbook.user.js) |
| `sakura` | Ink-wash twilight — brushed borders, washi ground, gold seal | [install](https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/themes/sakura/custom-duelingbook.user.js) |
| `void` | Pure black, hairline zones, one accent a side; built for low bitrate | [install](https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/themes/void/custom-duelingbook.user.js) |
| `arcade` | Phosphor and scanlines, blocky frames, pixel reticles | [install](https://raw.githubusercontent.com/Jazzzzzyyyyy/my-custom-db-theme/main/themes/arcade/custom-duelingbook.user.js) |

The script at the repo root is Neon Grid and updates itself, so if you already run it
you only need the other six. `themes/neon-grid/` is the same thing regenerated.

### Regenerating

```
python3 build_all.py          # all seven, assets + scripts
python3 build_theme.py --list # what is defined
```

A theme is one entry in `THEMES` in `build_theme.py`: eight colours plus three style
knobs — `frame` (bracket, double, dashed, cut, brush, block), `glyph` (diamond, cross,
circle, pixel, none) and `bg` (city, rays, grid, flat, paper, scanlines). `build_all.py`
rewrites each script's asset URLs, metadata and the `NEON_THEME` palette that drives
the CSS layer, so a new theme needs no hand-editing.

## Files

- **Field** — `field_zones2.svg`, `field_decks2.svg`, `background.svg`, `laser_sword.svg`
- **Phase** — `button_bg.svg`, `button_{red,blue}.svg`, `button_{red,blue}_lit.svg`
- **Turn** — `turn_background.svg`, `turn_{red,blue,yellow,green}.svg`, `white_glow.svg`
- **Counters** — `counter.svg`, `counter_glow.svg`
- **Profiles** — `profile_bg_{red,blue}.svg`
- **Builder** — `deck_constructor.svg`, `search.svg`
- **Buttons** (`_up` / `_over` / `_down` each) — `die_btn`, `coin_btn`, `token_btn`,
  `sort_btn`, `info_btn`, `search_prev_btn`, `search_next_btn`
- **Chrome** — `cell4.svg`, `cell_sel.svg`, `check.svg`, `radio.svg`, `combobox_arrow.svg`

## Notes

- **Four components are themed with CSS, not images.** DuelingBook rebuilt the phase
  buttons, turn indicator, deck constructor and card-search panel as gradient `<div>`s
  with no `<img>` inside. Custom DB still calls `.attr('src', …)` on them, which now
  writes to elements that have no `src` — so those settings do nothing on current
  DuelingBook, whichever URLs you put in them. This fork injects a `setNeonGridCss()`
  stylesheet instead, targeting the real classes (`.phase_inner.red/.blue`,
  `.phase.active`, `#turn .red/.blue`, `.deck_bg`, `.side_bg`, `.extra_bg`,
  `.search_bg`). The matching SVGs still ship, for reference and for anyone on an
  older build.

  Inert as a result: *Phase Button \** , *Turn Button \** (except Glow), *Deck
  Constructor Background Image Url*, *Deck Constructor Search Image Url*.

- **Master Rule 3 duels keep DuelingBook's own field art.** MR3 has no Extra Monster
  or Pendulum zones, so the Neon Grid layout would put brackets in the wrong places.
- **Five files have no settings field** — `cell4`, `cell_sel`, `check`, `radio`, and
  `combobox_arrow` are hard-coded inside `setDarkMode()` and
  `adjustElementsForDarkmode()`. The bundled script already points them here; the
  Import Settings route can't reach them.
- `@updateURL` and `@downloadURL` point at this repo, so upstream Custom DB releases
  won't silently overwrite the theme. To pick up the author's fixes, re-run the URL
  patch against a fresh copy of his script.

## Credit

Userscript by **Killburne** ([custom-duelingbook](https://github.com/killburne/custom-duelingbook/), MIT),
vendored here at v1.1.71 with asset URLs repointed. Artwork in `assets/` is original.

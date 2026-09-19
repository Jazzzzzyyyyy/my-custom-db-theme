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

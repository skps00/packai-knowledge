# Contributing

Thanks for helping document modded item mechanics. Two rules matter most:

1. **Mod knowledge only.** Tooltips, JEI/REI info pages, loot tables, recipes, attribute modifiers, guidebook pages. **Do not** add anything derived from a modpack's KubeJS/scripts — those differ per pack and are handled locally by the mod.
2. **Every fact needs a `source` and a `tier`** (A/B/C). Facts without provenance are rejected.

## Add an entry

1. Fork this repository.
2. Edit `mods/<namespace>.json` (create it if missing). One file per mod namespace; a file holds either a list `{"entries": [...]}` or a single entry object.
3. Fill in: `item`, `display`, `mod`, `applies_to`, then any of `obtain` / `use` / `worn`, plus `contributors` and `updated` (YYYY-MM-DD).
4. Add yourself to `contributors`.
5. Validate: `python scripts/validate.py` → must print `OK`.
6. Open a PR. CI runs the same validator (schema + required fields + duplicate keys).

## Tiers

- **A** — machine-checkable: loot table / recipe JSON in a mod jar, attribute modifier, datapack advancement. Quote the data.
- **B** — written by a human for this item: JEI info page, tooltip (including Shift-gated lines), guidebook page.
- **C** — written by a human, possibly incomplete: quest description. Answers mark these as "may not cover everything".

## Duplicates and conflicts

- Duplicate key = `item` + mechanism (`obtain`/`use`/`worn`) + normalized effect text. The validator **fails** on duplicates: merge them instead, combining `source`s.
- **Conflicting facts are not duplicates.** If two sources disagree (e.g. 1% vs 5%), keep both facts and set `"conflict": true` on each. Never silently drop one.

## Style

- lowercase ids (`namespace:path`), no display names in `item`.
- English or Chinese both fine in `effect`; keep it short and factual.
- No game-balance opinions, no strategy advice — mechanics only.

## Removing / correcting

If a mechanic changed in a newer mod version, update the entry and bump `updated`, or set `applies_to.mod_versions`. Do not delete history silently; explain the change in the PR description.

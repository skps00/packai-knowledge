# packai-knowledge

Community knowledge entries for **mod items** used by the [Pack AI Assistant](https://www.curseforge.com/minecraft/mc-mods/pack-ai-assistant-paia) Minecraft mod: *how you get an item* and *what it does*, for mechanics that are not visible in normal recipe/book data.

> **Status: early skeleton.** Schema + tooling land first; entries are being drafted from mod-side evidence (tooltips, JEI info pages, loot tables, attribute modifiers, mod guidebooks).

## Scope — important

- ✅ **Mod knowledge only**: tooltip lines (including Shift-gated ones), JEI info pages, loot tables / recipe JSON inside mod jars, attribute modifiers, mod guidebook pages.
- ❌ **No KubeJS / pack-script knowledge.** Scripted mechanics differ per modpack, so each pack resolves them locally. Nothing from `kubejs/**` belongs in this repository.
- ❌ **No ids that exist only because a modpack registered them** (e.g. a namespace created by a pack's KubeJS scripts). If no mod jar provides the item, it is not mod knowledge — an entry keyed to such an id is rejected in review.

## Layout

```
index.json                     mod list + per-file sha + schema version
mods/<namespace>.json          entries for one mod (one file per mod; easy diffs)
items/<namespace>/<path>.json  optional single-item files (for on-demand fetch)
schema/entry.schema.json       JSON Schema for one entry
examples/example-entry.json    a complete example
scripts/validate.py            schema + duplicate-key validation (runs in CI)
```

## Entry format (one item = one entry)

```json
{
  "item": "create:goggles",
  "display": {
    "en_us": "Engineer's Goggles",
    "zh_cn": "工程师护目镜"
  },
  "mod": "create",
  "applies_to": {
    "mc": "1.19.2",
    "loader": "forge",
    "mod_versions": [
      "0.5.x"
    ]
  },
  "obtain": [
    {
      "type": "craft",
      "source": "mod:recipe_json",
      "tier": "A"
    }
  ],
  "use": [
    {
      "trigger": "wear_in_head_slot",
      "effect": "shows the Goggles overlay (stress / capacity / block info)",
      "source": "mod:tooltip",
      "tier": "B"
    }
  ],
  "worn": [
    {
      "slot": "head",
      "effects": [
        "shows the Goggles information overlay while worn"
      ],
      "source": "mod:tooltip",
      "tier": "B"
    }
  ],
  "notes": "EXAMPLE FILE — the shape is what matters; the values are illustrative placeholders, verify against the mod before publishing.",
  "contributors": [
    "skps00"
  ],
  "updated": "2026-09-14"
}
```

### Provenance tiers (required on every fact)

| tier | meaning | typical source |
|---|---|---|
| **A** | machine-checkable — taken from data, may be quoted directly | loot table / recipe JSON in a mod jar, attribute modifier, datapack advancement |
| **B** | written by a human *for this item* | JEI info page, item tooltip (incl. Shift lines), guidebook page |
| **C** | written by a human, possibly incomplete | quest description |

Rules:
- Every fact carries `source` and `tier`.
- **A/B facts always outrank C facts** in answers; C is marked as "quest description (may not cover everything)".
- **Duplicates:** one entry per `item` + `mechanism type` + normalized effect text. `scripts/validate.py` fails on duplicate keys.
- **Conflicts are not duplicates:** if two sources disagree (e.g. different drop chances), keep **both** facts with their own `source`/`tier` and add `"conflict": true`. Never silently drop one.

## How the mod consumes this

The mod checks this repository only when it cannot answer an item from local data, and it requests a single item file (sends the item id only — no chat, no player data). Results are cached locally with ETag; offline use falls back to the cache and to local pack data.

## Contributing

1. Fork, add or edit `mods/<namespace>.json`.
2. Run `python scripts/validate.py` — it must print `OK`.
3. Open a PR. CI re-runs the validator (schema + duplicate keys).
4. Cite where the fact comes from in `source` — PRs without a source are rejected.

See `CONTRIBUTING.md` for details.

---
name: update-acf-fields
description: >-
  Surgically update ACF local JSON field group files: change only search-field
  property values (short_description, button_text, and related keys), bump
  modified to the current Unix timestamp, preserve exact file formatting and ACF
  slash escaping. Use when the user invokes /update-acf-fields, asks to update
  ACF JSON, search fields, or acf-json group files.
disable-model-invocation: true
---

# Update ACF Fields (local JSON)

Surgical edits to ACF field-group JSON under `acf-json/`. **Never re-serialize the file.**

## What counts as a search field

Update **only** fields the user asked for that match one of:

| Match | Example |
|-------|---------|
| `"name": "short_description"` | Teaser / excerpt textarea |
| `"name": "button_text"` | Teaser / CTA label |
| Instructions mention search | `"instructions": "...search results."` |

Do **not** edit other fields, layouts, location rules, tabs, clones, or group metadata unless the user explicitly asks — see **Edit scope** below.

## Edit scope

### Default (no extra permission)

Change only the search-field properties the user requested, typically:

- `default_value`, and translation-plugin defaults if present (e.g. `pll_default_value`)
- `label`, `instructions`, `placeholder`
- `maxlength`, `rows`

Never rename `key` or `name`. Never reorder fields. Never change `type` or structural keys unless the user asked.

### Explicit user request — do it

When the user **clearly specifies** a broader change, apply it across the scope they named. Examples:

- “Update all text fields to wysiwyg” → change `"type": "text"` → `"type": "wysiwyg"` on every matching field in the named group(s), plus any sub-keys that type requires (`tabs`, `toolbar`, etc.).
- “Set wrapper widths to 30, 30, 40 on these three fields” → edit `wrapper.width` on those fields only.

Follow their wording for **which fields** and **which properties**. Still use surgical StrReplace; still preserve formatting and escaping rules below.

### Suggested extras — ask first

While editing, you **may notice** inconsistencies (e.g. sibling rows use `"width": "30"` / `"30"` / `"40"` but the target row has `"width": ""`). **Do not apply** those fixes silently.

1. Finish the requested changes.
2. Briefly describe what you noticed and what you would change.
3. Ask whether to apply the extra edits.
4. Apply only after the user confirms.

### Hard limits (even with permission)

- Do not re-serialize or reformat the file.
- Do not rename `key` / `name` unless the user explicitly asks.
- Do not reorder fields unless the user explicitly asks.

## Formatting rules (critical)

ACF writes JSON with `JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE`. PHP escapes `/` as `\/` inside strings. **Do not normalize or pretty-print.**

| Do | Don't |
|----|-------|
| Read the file; copy existing escape style on nearby lines | `json.dumps()`, `JSON.stringify()`, `jq`, Prettier, or full-file rewrite |
| Use **StrReplace** with exact old → new strings | Re-indent, reorder keys, or trim/add blank lines |
| Keep 4-space indent, trailing newline, key order | Touch tabs, toolbars, wrappers, or unrelated strings **without user permission** |
| Use `\/` for `/` in strings when the file already does | Add `\\`, `\\\/`, or double-escape backslashes |

**Slash escaping:** If the line already has `d\/m\/Y`, keep one backslash before each slash. Never produce `d\\/m\\/Y` or `d\\\\/m\\\\/Y`.

**Example — correct surgical edit:**

```json
"default_value": "Read more",
```

If the new value contains `/`, match file style: `"Visit https:\/\/example.com"`.

## Workflow

1. **Locate** the target `acf-json/group_*.json` (user path or search by field `key` / group `title`).
2. **Read** the file; note exact whitespace and escaping on the lines you will change.
3. **Edit** via StrReplace (one property per replace when possible): default = search-field keys only; broader scope only when the user asked or confirmed (see **Edit scope**).
4. **Bump `modified`** to current Unix timestamp (seconds):

   ```bash
   python3 ~/.cursor/skills/update-acf-fields/scripts/bump-modified.py path/to/group_*.json
   ```

   Or StrReplace the existing `"modified": <digits>` line — use the script when editing multiple files.

5. **Verify** with a diff: changed lines should be only the intended values + `modified`. No mass reformatting.

## Checklist before finishing

- [ ] Scope matches request: default search-field edits only, or explicit/confirmed extras
- [ ] No extra `\\` introduced
- [ ] Tabs, spacing, and unrelated keys untouched (except user-requested or confirmed edits)
- [ ] `"modified"` is current Unix time
- [ ] Diff is minimal

## Finding targets in the current repo

Do not assume fixed paths or group keys. Discover from the workspace:

1. Search `acf-json/` for `"name": "short_description"`, `"name": "button_text"`, or instructions containing `search results`.
2. If the user names a group, match by `title` or filename they provide.
3. Optional: grep the theme for REST/search helpers (e.g. `search_fields`, `get_field('short_description'`) to see which meta keys the frontend reads — field-group JSON defines the **admin field definition**, not live post content.

## Additional resources

- [examples.md](examples.md) — before/after edit patterns

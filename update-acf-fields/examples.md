# ACF JSON edit examples

## Good: single property swap

**Before:**
```json
            "default_value": "",
            "maxlength": "",
            "rows": 3,
            "placeholder": "",
            "new_lines": "br",
            "translations": "copy_once",
            "pll_default_value": ""
        },
        {
            "key": "field_example_button",
            "label": "Button text",
            "name": "button_text",
```

**Change only `default_value` on `short_description`:**
```json
            "default_value": "Read more",
```

Everything else — indentation, surrounding keys, trailing commas — stays identical.

## Good: bump modified

**Before:** `"modified": 1710000000`  
**After:** `"modified": 1748188800` (current `date +%s`)

Use `scripts/bump-modified.py` so you don't hand-type timestamps when editing several files.

## Bad: re-serialized file

```diff
-            "instructions": "Used in teasers and search results.",
+      "instructions": "Used in teasers and search results.",
```

Indent changed → reject this approach.

## Bad: double-escaped slashes

```diff
-            "display_format": "d\/m\/Y",
+            "display_format": "d\\/m\\/Y",
```

Extra backslashes break ACF's expected on-disk format.

## Bad: touched unrelated tab field

```diff
             "type": "tab",
-            "placement": "top",
+            "placement": "left",
```

Out of scope unless the user explicitly asked.

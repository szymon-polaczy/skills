# Coverage playbook

Every test suite must be **thorough by design**, not a single happy path on one screen. This applies to any feature — admin tools, front-end flows, blocks, forms, APIs.

The parent agent owns the coverage matrix. Subagents feed rows; the parent must not ship a doc until the matrix is complete or every skipped cell has a written reason.

---

## Three mandatory dimensions

Discover and document all three. If a dimension does not apply, state **N/A — why** in the doc (one line).

### 1. Surfaces (where the feature appears)

All distinct **entry points** a user or admin can hit — not just the obvious primary screen.

Find surfaces by tracing:

- Script/style enqueue conditions (`wp_enqueue_scripts`, `admin_enqueue_scripts`, screen `$hook_suffix`)
- `add_menu_page`, `add_submenu_page`, removed/hidden menus
- Hooks tied to screen IDs (`load-upload.php`, `post.php`, `acf/options_page`)
- JS that mounts UI into modals, sidebars, toolbars, bulk actions, inline editors
- Shortcodes, blocks, widgets, REST consumers
- Front-end templates vs wp-admin vs network admin vs customizer

List every surface separately. Examples of surface *types* (use what discovery finds — do not assume these exist):

| Type | Question to answer |
|------|-------------------|
| Dedicated screen | Is there a standalone admin or front-end page? |
| Embedded in edit flow | Does it appear when editing a post/page/CPT? |
| Options / settings | Does it appear on global or per-site options pages? |
| Modal / popup / frame | Does it load inside WP media modal, ACF picker, Thickbox, etc.? |
| List vs detail vs upload | Grid, list, single-item, create/new flows — same or different UI? |
| Bulk / batch actions | Toolbar actions, row actions, multi-select flows? |

**Failure mode to avoid:** testing only one surface (e.g. one admin URL) when code enqueues or hooks on others.

### 2. Contexts (where behavior differs)

All **scopes** in which the same surface can behave differently.

Find contexts by tracing:

- `switch_to_blog`, `get_current_blog_id`, network vs site admin
- Capability checks (`current_user_can`, role checks)
- Options/feature flags per site or network
- “Global” vs “local” site pairs in multisite
- Master vs subsite URL prefixes (front-end or admin redirects)
- Logged-in vs guest; staging vs production-only config

Build a list of **representative contexts** to test — not necessarily every blog ID, but enough to prove cross-context behavior:

- At least **two contexts** when code shows context-dependent logic
- At least **one “global/network” and one “local/subsite”** when multisite or shared-library patterns exist
- Do not collapse everything into a single `base_url/...` path without checking code for branches

**Failure mode to avoid:** one subsite smoke test tagged “subsite context” while global admin, other subsites, and options pages are untested.

### 3. Presence and absence (negative coverage)

Where the feature **must not appear** or must **behave differently** — explicit tests or documented N/A.

Find absence rules by tracing:

- Early `return` in enqueue or render hooks
- `if ( ! is_main_site()`, blog ID allowlists/denylists
- Capability failures, `wp_die`, hidden menu items
- Screens deliberately excluded in code comments or conditions

Every restriction in code should map to either:

- A test case (“expect tag filter **absent** on `{screen}` for `{context}`”), or
- **Intentional omission** with reason in the coverage matrix

**Failure mode to avoid:** only asserting the feature works where it should, never asserting it is hidden where code says it should be.

---

## Coverage matrix (required before writing test cases)

Parent fills this after Wave 1–2 merge. Cells = expected behavior: **works**, **hidden**, **different**, **N/A**.

```markdown
### Coverage matrix

| Surface \ Context | {Context A} | {Context B} | {Context C} |
|-------------------|-------------|-------------|-------------|
| {Surface 1}       | works       | hidden      | —           |
| {Surface 2}       | works       | works       | different   |
| {Surface 3}       | N/A         | works       | —           |

**Intentional omissions**
| Cell | Reason |
|------|--------|
| {Surface X} × {Context Y} | {e.g. duplicate of Surface 1; no automated upload} |
```

Rules:

- Every **works** cell → at least one `###` test case (or explicit shared test covering multiple cells)
- Every **hidden** cell → negative test case
- Every **different** cell → test case noting expected difference
- Empty cells without a row in **Intentional omissions** → doc is **incomplete**

---

## Wave 2 agent: Coverage & surfaces (always run)

Launch **in parallel** with other Wave 2 agents — **not optional**.

**Task:** Return surfaces, contexts, absence rules, and a draft matrix.

**Return format:**

```markdown
### Surfaces
| ID | Surface | How triggered | Source file/hook |

### Contexts
| ID | Context | How identified | Example URL/admin path |

### Absence rules
| Surface | Context | Expected | Source (file:line or hook) |

### Draft matrix
(table)

### Coverage risks
- {e.g. "only upload.php traced; acf/options_page enqueue not yet verified"}
```

---

## Turning matrix into test doc sections

Organize test groups so coverage is obvious — pick one primary axis:

- **By surface** — each `##` group is a surface; tests run across relevant contexts inside
- **By context** — each `##` group is a site/role; tests hit all surfaces inside

Within each group:

1. Positive: feature works as expected
2. Negative: feature absent or blocked (if matrix says **hidden**)
3. Variant: behavior differs (if matrix says **different**)

Use **paths to check** lists when the same assertion applies to multiple contexts:

```markdown
- paths to check
	- `base_url/{context-a}/...`
	- `base_url/{context-b}/...`
- visit each path
- expect {assertion per context or shared assertion}
```

Do not duplicate ten identical tests — but do not skip contexts to avoid duplication when assertions differ.

---

## Thoroughness gate (parent, before user approval)

Before presenting the doc, verify:

```
- [ ] Surfaces dimension filled or N/A with reason
- [ ] Contexts dimension filled or N/A with reason
- [ ] Absence rules traced from code or marked "none found"
- [ ] Coverage matrix complete; no unexplained empty cells
- [ ] Every "works" / "hidden" / "different" cell has test coverage or intentional omission
- [ ] Summary "URLs touched" counts all admin + front + modal flows, not one page
- [ ] Embedded flows (modals, options pages, inline editors) explicitly listed if code enqueues there
```

If the suite would only test one surface × one context, **stop and expand discovery** — launch another Wave 2 agent targeting enqueue hooks, ACF location rules, or admin screen registration before writing the doc.

---

## Agent prompt snippet (Coverage agent)

```
Feature: {name}
Theme: {THEME}
Keywords: {list}
Known files from merge: {file list}

Task: Coverage & surfaces agent.

Find ALL surfaces (screens, modals, options pages, embeds), ALL contexts
(sites, roles, global vs local) where behavior differs, and ALL absence
rules (where feature must NOT show).

Return the Coverage agent return format from coverage-playbook.md.
Do not write the final test doc. Flag coverage risks explicitly.
```

# Discovery playbook

Start from the user’s words. Follow signals in code and on the running site. **Do not assume** any plugin, architecture, or project pattern until you find evidence.

**Parallelize search, serialize synthesis.** The parent agent orchestrates; subagents return slices. See parallel sections below.

---

## Step 0 — Parent only (sequential)

Before launching agents:

1. Resolve `THEME`, `SPEC_DIR`, `SUPPORT_DIR`, `baseUrl`
2. Expand keywords from the feature request (names, slugs, classes, hooks)
3. Pass feature name, keywords, and `THEME` into every agent prompt

---

## Step 1 — Wave 1: core discovery (always parallel)

Launch **all four agents in one message**. Each returns its section only — no test doc, no Cypress.

### Agent A — Code trace

Search under `THEME` (+ follow imports into plugins/packages if theme delegates):

| Layer | How to find it |
|-------|----------------|
| **PHP entry points** | `add_action`, `add_filter`, classes/files matching keywords |
| **Templates** | `templates/`, `views/`, `*.blade.php`, `get_template_part`, page templates |
| **Forms** | Plugin hooks (`gform_`, `wpcf7_`, `nf_`, custom submit hooks), shortcodes, `<form` |
| **Blocks / components** | Block registration APIs, `blocks/`, `acf_register_block`, partials |
| **Front-end JS** | Theme scripts, component JS, data attributes, client routers |
| **REST / AJAX** | `register_rest_route`, `wp_ajax_`, fetch/XHR in JS |
| **Shortcodes** | `add_shortcode`, shortcode usage in templates |

**Return format:**
```markdown
### Files
- path — role
### Open questions
- ...
```

### Agent B — Config inventory

From files Agent A finds (or parallel grep if Agent A not done — prefer waiting for merge):

- Form/plugin IDs, field IDs, option keys
- Custom field names and where read
- Constants, feature flags, user meta
- CMS content required for tests (pages, posts, products)

**Return format:**
```markdown
### Config
- key/id — where used
### Test data dependencies
- ...
```

### Agent C — URL discovery

From code (parallel grep — does not need Agent A to finish):

- Page slugs, redirects, rewrite rules, form actions
- Confirmation routes, archive URLs, REST endpoints
- Candidate paths only — live status comes in Wave 3

**Return format:**
```markdown
### URLs
| Path | Source file | Role: entry/intermediate/confirmation/API |
```

### Agent D — Existing test context

Read-only scan:

- Human-readable test docs under `THEME`
- `SUPPORT_DIR` custom commands and config
- One representative spec in `SPEC_DIR` for conventions

**Return format:**
```markdown
### Existing patterns
- doc/command/spec — what to reuse
### Cross-cutting rules (only if applicable to this feature)
- ...
```

---

## Step 1.5 — Wave 1.5: external context (parent + optional agents)

**After Wave 1 merge, before Wave 2.**

Follow [external-context-playbook.md](external-context-playbook.md):

1. Build **External touchpoints** table from merged Wave 1 files (plugins, mu-plugins, services)
2. Decide per touchpoint: local docs sufficient? web search needed? skip with reason?
3. Gather context in parallel (local readme, plugin source skim, WebSearch/WebFetch)
4. Append **External context** + **External-driven coverage notes** to discovery map
5. Pass enriched map into Wave 2 Coverage agent prompt

If no external touchpoints → one-line “none” and proceed.

---

## Step 2 — Wave 2: coverage + conditional deep-dives (parallel)

Launch **in one message**:

### Agent E — Coverage & surfaces (**always**)

See [coverage-playbook.md](coverage-playbook.md). Surfaces, contexts, absence rules, draft matrix, coverage risks.

**Include Wave 1.5 external context** in the agent prompt when present — plugin admin rules and multisite behavior often define surfaces the theme alone does not show.

**Do not skip** because the feature “looks like one admin page” — trace enqueue hooks and screen conditions first.

### Agents F+ — Conditional deep-dives (0–N)

| Signal | Agent task | Return |
|--------|------------|--------|
| Block/component | Registration, templates, static refs, CMS-only usage | Files + usage locations |
| Form + backend | Submit hooks, handlers, automatable vs not | Handler map + gaps |
| E-commerce | Catalog, product, cart, checkout, account surfaces | URLs + templates |
| Multisite / URL prefixes | Path building, site pairs, rewrite rules | Prefix rules + URL variants |

Skip conditional agents with no signal. **Never skip Agent E (Coverage).**

---

## Step 3 — Parent merge (sequential)

Combine Wave 1 outputs into discovery map. Deduplicate files and URLs. Flag conflicts for one user question or follow-up grep.

Then run **Step 1.5 (external context)** before launching Wave 2.

After Wave 2+3, merge again with external notes and URL verification.

---

## Step 4 — Wave 3: live URL verification (parallel batches)

Split merged URL list into batches (~5–10 per agent). Launch batch agents **in one message**.

Each batch agent (browser MCP preferred):

| Check | Record |
|-------|--------|
| HTTP status | 200, 301, 302, 404 |
| Final URL after redirects | pathname + query |
| Auth gate | redirect to login? return URL param? |
| Visible UI | entry points, empty/error states |

**Return format:**
```markdown
### URL verification
| URL | Status | Final path | Auth | Notes |
```

If live check unavailable: parent notes `live verification pending` and continues.

---

## Step 5 — Flows, matrix, and branches (parent, sequential)

1. Finalize **coverage matrix** from Agent E + code merge
2. Run [thoroughness gate](coverage-playbook.md#thoroughness-gate-parent-before-user-approval)
3. For each matrix cell with **works** / **hidden** / **different**, draft test cases

For each verified user-visible path:

```
Entry URL(s)
  → Preconditions (only those that apply)
  → User steps
  → Expected end state
  → Not automatable side effects
```

List branches: validation errors, empty states, permission denied, alternate paths.

---

## Step 6 — Cross-cutting concerns (parent, sequential)

Check whether this feature touches patterns from Agent D’s findings. Pull in only applicable rules — no generic multisite/shop/CRM sections unless discovered.

---

## Discovery map (parent output, before writing doc)

```markdown
## Feature: {name}
Theme: {THEME}
Cypress: {SPEC_DIR}

### External context
(touchpoints, docs consulted, test-relevant findings — or "none")

### Surfaces
- id — name — hook/source

### Contexts
- id — name — example path

### Coverage matrix
(table)

### Files
- path — role

### Config
- ...

### URLs
| URL | Preconditions | Status | Notes |

### Flows
1. ...

### Not automated
- ...

### Open questions
- ...
```

Resolve open questions, then write `THEME/test_docs/{feature-slug}.md`.

---

## Agent prompt snippet (copy into Task calls)

```
Feature: {feature name}
Theme: {THEME path}
Keywords: {comma-separated}
Your task: {Agent A|B|C|D|External context|Web research:{dep}|E Coverage|deep-dive name}

Search read-only. Return ONLY the return format for your agent type.
Do not write the test doc. Do not implement Cypress.
```

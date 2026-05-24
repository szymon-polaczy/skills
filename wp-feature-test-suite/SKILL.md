---
name: wp-feature-test-suite
description: >-
  Discovers all code, ACF/options, URLs, and user paths for a WordPress theme
  feature, writes a human-readable test suite doc in THEME/test_docs/, confirms
  with the user, then generates Cypress tests in that theme's Cypress setup.
  Use when the user wants to test a feature, create a test suite, trace a
  user-facing flow, or says "human-readable testing suite".
disable-model-invocation: true
---

# WordPress Feature Test Suite

Two-phase workflow: **discover + document**, then **implement Cypress** (only after user approval).

Read supporting files when needed:
- [doc-template.md](doc-template.md) — output structure
- [discovery-playbook.md](discovery-playbook.md) — how to trace a feature
- [coverage-playbook.md](coverage-playbook.md) — **mandatory** surfaces × contexts × absence matrix
- [external-context-playbook.md](external-context-playbook.md) — plugins/services docs + web research after Wave 1
- [cypress-playbook.md](cypress-playbook.md) — doc → spec implementation

## Phase 0 — Resolve theme and paths

Before any discovery, resolve these paths once and reuse them:

### 1. Theme root (`THEME`)

Pick the active theme directory (contains `style.css` or is clearly the custom theme):

1. Theme path from open files or user mention
2. Else `wp-content/themes/<name>/` for the project’s active/custom theme
3. If ambiguous, ask which theme

### 2. Test doc output

```
THEME/test_docs/{feature-slug}.md
```

Create `test_docs/` on first use. Slug from feature name (`sugar-forms`, `compare-section-block`).

### 3. Cypress root (`CYPRESS_ROOT`)

Locate Cypress for **this theme only** — do not assume `resources/`, `inc/`, or a fixed subfolder.

1. Find `cypress.config.js` under `THEME` (theme root or any subdirectory)
2. Read `e2e.specPattern` and `e2e.supportFile` — they define where specs and support live
3. If theme root has a wrapper config (re-exports a nested config), follow resolved paths
4. Record:
   - `CYPRESS_ROOT` — directory containing the `cypress/` folder (or parent of `specPattern`)
   - `SPEC_DIR` — e2e spec folder (usually `.../cypress/e2e/`)
   - `SUPPORT_DIR` — support folder (usually `.../cypress/support/`)
   - `CYPRESS_CWD` — directory to run `npm run cypress:run` from (where `package.json` + config live)
   - `baseUrl` — from the effective config

New spec path: `SPEC_DIR/{feature-slug}.cy.js`

### 4. Reference doc (optional)

If the theme already has a human-readable test doc under `THEME`, read it for cross-cutting rules that might apply. Copy only what this feature needs — do not assume every project has multisite, shop pairs, or special test data unless discovery confirms it.

## Phase 0 — Intake

Extract from the user request:

- Feature name and scope
- Auth or state preconditions if obvious (guest, logged-in, cart, etc.)
- Sites / locales to cover only if the project uses multisite, prefixes, or multiple domains

If scope is vague, ask **one** focused question, then proceed.

## Phase 1 — Discovery (read-only, parallel)

Follow [discovery-playbook.md](discovery-playbook.md). **Parallelize search; serialize synthesis.**

### Orchestration rules

1. Parent resolves `THEME`, paths, and keywords first — then fan out
2. Launch independent discovery agents **in one message** (multiple Task calls), not sequentially
3. Each agent returns a structured slice (files, config, URLs) — not the final doc
4. Parent merges results, then writes flows and the test doc alone
5. Do not start Cypress or the test doc until merge is complete

### Wave 1 — always parallel (4 agents)

| Agent | Task |
|-------|------|
| Code trace | PHP/JS/templates, hooks, handlers under `THEME` |
| Config inventory | Fields, options, form IDs, constants |
| URL discovery | Slugs, redirects, rewrites, form actions, REST |
| Existing test context | Test docs under `THEME`, Cypress support + spec patterns |

Use `subagent_type: explore`, `readonly: true`.

### Wave 1.5 — external context (after Wave 1 merge, before Wave 2)

Parent merges Wave 1, then runs [external-context-playbook.md](external-context-playbook.md):

1. List external touchpoints (plugins, mu-plugins, services outside `THEME`)
2. For each: check local readme/docs in repo; **web search only when** that improves surfaces, selectors, setup, or matrix cells
3. Merge findings into discovery map — Wave 2 agents receive this context

Skip quickly if the feature is theme-only. Record “no external deps” in the map.

Optional: one **External context agent** (+ parallel **Web research** agents per dependency when needed) in one message.

### Wave 2 — parallel (always + conditional)

Launch **in one message**:

| Agent | Required? | Task |
|-------|-----------|------|
| **Coverage & surfaces** | **Always** | All entry points, contexts, absence rules, draft matrix — see [coverage-playbook.md](coverage-playbook.md) |
| Block / form / shop / multisite deep-dives | Only if signaled | From Wave 1 keywords or code |

A doc that only tests one screen × one context is **incomplete**. Expand discovery before writing.

### Wave 3 — live URL batches (parallel)

Merge URL lists from Wave 1+2, split into batches (~5–10 URLs), verify in parallel via browser MCP or requests. Skip if unavailable — note in doc.

### Wave 4 — synthesize (parent, sequential)

Merge → **coverage matrix** (mandatory) → flows/branches → gaps → write `THEME/test_docs/{feature-slug}.md`.

Run the [thoroughness gate](coverage-playbook.md#thoroughness-gate-parent-before-user-approval) before presenting to the user.

Discovery map areas:

| Area | What to capture |
|------|-----------------|
| Surfaces | Every screen, modal, embed, options page — not just the primary URL |
| Contexts | Sites, roles, global vs local — every scope where behavior differs |
| Absence | Where feature must be hidden or blocked |
| Code | PHP/JS/templates; hooks; handlers |
| Config | Fields/groups, options, IDs, constants |
| URLs | All paths per surface × context |
| Flows | Branches, preconditions, end states |
| Gaps | Backend-only behavior not suitable for Cypress |
| External | Plugins/services; docs consulted; integration limits |

## Phase 1 — Write test doc

Write `THEME/test_docs/{feature-slug}.md` using [doc-template.md](doc-template.md).

In the doc header, use **paths relative to THEME**:

```markdown
Cypress spec: `{path from THEME to SPEC_DIR}/{feature-slug}.cy.js`
```

Include a **Scope & discovery summary** and a **Coverage matrix** (see [coverage-playbook.md](coverage-playbook.md)). List all surfaces and contexts in the summary — not a single admin URL count.

## Approval gate (mandatory)

After writing the doc:

1. Present summary: **surfaces covered**, **contexts covered**, **negative/absence tests**, matrix omissions, known gaps
2. Ask the user to approve before any Cypress work
3. **Do not** create or edit `.cy.js` files until confirmed
4. On rejection: revise the doc only, re-present

## Phase 2 — Cypress (after approval)

Follow [cypress-playbook.md](cypress-playbook.md).

Optional parallel pre-read (one message): one agent reads existing specs for style, another reads support modules — then parent writes spec + helpers sequentially.

1. Create `SPEC_DIR/{feature-slug}.cy.js`
2. Reuse existing custom commands from `SUPPORT_DIR` — read what is already there
3. Add `{feature-slug}-helpers.js` in support only when steps are reused across tests
4. Extend existing config modules (do not duplicate path constants)
5. Map each `###` test case in the doc → one `it(...)` or a shared helper
6. Spec header must reference the test doc:

```javascript
/**
 * {Feature Title}
 * Spec: test_docs/{feature-slug}.md
 */
```

Optional: run Cypress from `CYPRESS_CWD` with `--spec` pointing at the new file.

## Task progress checklist

Copy and track:

```
- [ ] Theme root and Cypress paths resolved
- [ ] Wave 1 discovery agents merged
- [ ] Wave 1.5 external context checked (local docs / web if needed)
- [ ] Wave 2 coverage agent merged (surfaces × contexts × absence)
- [ ] Coverage matrix complete; thoroughness gate passed
- [ ] URL batches verified (if live check ran)
- [ ] Discovery map complete
- [ ] test_docs/{feature-slug}.md written
- [ ] User approved
- [ ] Cypress spec + helpers implemented
- [ ] (Optional) Spec run
```

## Usage examples

```
Use wp-feature-test-suite: map and test the contact form submission flow
```

```
Use wp-feature-test-suite: test the hero banner block wherever it is used
```

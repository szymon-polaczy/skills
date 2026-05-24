# External context playbook

After **Wave 1 merge**, before Wave 2 coverage work. Determine whether the feature depends on code **outside the theme** — plugins, mu-plugins, SaaS APIs, WP core subsystems — and whether extra documentation is needed to write accurate tests.

**Do not web-search by default.** Search only when the checklist below says it will improve the test suite.

---

## When to run

```
Wave 1 (code, config, URLs, existing tests)
  → Wave 1 merge (parent)
  → **External context check (this playbook)**
  → Wave 2 (coverage + deep-dives) — uses enriched context
  → Wave 3 (live URLs)
  → Wave 4 (synthesize doc)
```

---

## Step 1 — Identify external touchpoints (parent, from Wave 1 merge)

Scan merged files and config for dependencies outside `THEME`:

| Signal | Examples |
|--------|----------|
| Plugin paths | `wp-content/plugins/{name}/`, `mu-plugins/` |
| Plugin APIs | `GFForms`, `WC()`, `acf_`, third-party class names |
| Hooks owned elsewhere | `gform_*`, `woocommerce_*`, plugin-prefixed actions |
| Network / multisite APIs | `switch_to_blog`, shared library plugins |
| External services | CRM, payment, CDN, captcha, search SaaS |
| WP core subsystems | Media modal, REST, cron, user caps — when behavior is non-obvious |

**Return format (internal):**

```markdown
### External touchpoints
| Name | Type | Path or service | How feature uses it | Local docs? |
|------|------|-----------------|---------------------|-------------|
| {plugin} | plugin | wp-content/plugins/... | {hook/class} | yes/no/unknown |
```

If the table is empty or only standard WP/theme code → **skip to Wave 2** (note “no external deps” in discovery map).

---

## Step 2 — Do we need more documentation?

For each external touchpoint, ask:

| Question | If yes → |
|----------|----------|
| Does plugin behavior affect **which surfaces/contexts** exist? | Read docs — enqueue rules, admin screens, multisite behavior |
| Does it define **non-obvious selectors, URLs, or AJAX actions**? | Read docs or plugin source README |
| Does it require **specific setup** (license, network activation, API keys)? | Document in test data + **Not automated** |
| Is integration **custom/wrapper code** on top of the plugin? | Read **both** plugin docs and theme wrapper |
| Would guessing cause **wrong coverage matrix cells**? | Must research before Wave 2 |

**Skip web search when:**

- Theme code fully explains the behavior and tests only assert theme wrappers
- Plugin is trivially used (single `get_field` with no special behavior)
- Existing project test docs already cover the integration

**Use web search when:**

- Local plugin folder has no README / unclear behavior
- Official docs explain admin flows, hooks, or multisite rules not obvious from grep
- Version-specific behavior matters (check plugin version in repo if present)
- External SaaS API shapes test boundaries (what Cypress can vs cannot see)

---

## Step 3 — Gather context (parallel where possible)

Launch in **one message** when multiple sources needed:

### 3a — Local documentation (prefer first)

Read-only, no web until local is insufficient:

| Source | Look for |
|--------|----------|
| `wp-content/plugins/{plugin}/readme.txt` | Features, admin URLs, hooks |
| `README.md`, `docs/` in plugin folder | Setup, multisite, filters |
| Inline docblocks on classes/hooks the feature calls | Parameters, side effects |
| Project docs under `THEME/test_docs/` or theme README | Prior test conventions for this plugin |
| `human-readable*.md` anywhere in project | Cross-cutting plugin assumptions |

Agent task: summarize **test-relevant** facts only — admin paths, hooks, known limitations, multisite notes.

### 3b — Web search (when Step 2 says yes)

Use WebSearch / WebFetch for **specific** queries — not generic “how does WordPress work”.

Good queries:

- `{plugin name} WordPress admin media modal hooks`
- `{plugin name} multisite shared library documentation`
- `{service} test mode sandbox API`

Fetch official docs or developer references when available. Prefer plugin author domain over random blog posts.

**Parallel:** one search/fetch focus per external touchpoint (max ~3 concurrent unless user scope is huge).

### 3c — Plugin source skim (when docs are thin)

Readonly `explore` agent on `wp-content/plugins/{plugin}/` limited to:

- Admin menu registration
- `admin_enqueue_scripts` / `wp_enqueue_scripts` conditions
- Public hooks the theme attaches to
- Option keys and default behavior

Do not read entire plugin codebase — target files Wave 1 already pointed at.

---

## Step 4 — Merge back into discovery context

Add to the discovery map before Wave 2:

```markdown
### External context
| Dependency | Source (local doc / web / source skim) | Test-relevant findings |
|------------|----------------------------------------|-------------------------|
| {name} | {readme.txt / URL} | {bullet facts} |

### External-driven coverage notes
- {e.g. "Plugin adds media tab only on main site — matrix row needed"}
- {e.g. "Placeholder attachments resolve on save — assert network ID via UI not DB"}

### External-driven gaps (Not automated)
- {license activation, file sync to CDN, etc.}

### Research skipped
| Dependency | Reason |
|------------|--------|
| {name} | {theme code sufficient / already in project docs} |
```

Wave 2 **Coverage agent** prompt must include the **External context** section so surfaces/contexts reflect plugin behavior, not only theme files.

---

## Step 5 — Test doc section (when external deps exist)

In `THEME/test_docs/{feature-slug}.md`, add under the summary (only if Step 1 found touchpoints):

```markdown
**External dependencies**
- **{Plugin/service}:** {one-line role}
  - Docs consulted: {local path or URL}
  - Affects tests: {surfaces, setup, not-automated items}
```

Do not paste full plugin documentation — only facts that change test design.

---

## Thoroughness check (external)

Before Wave 2:

```
- [ ] External touchpoints listed or explicitly "none"
- [ ] Each non-trivial touchpoint: local docs checked OR web search OR skip reason recorded
- [ ] Findings merged into discovery map for Coverage agent
- [ ] Setup/license/backend limits in Not automated if docs say so
```

---

## Agent prompt — External dependencies (Wave 1.5)

```
Feature: {name}
Theme: {THEME}
Wave 1 merge summary: {files, plugins referenced}

Task: External context agent.

List external touchpoints (plugins, mu-plugins, services). For each:
1. Check local readme/docs in the repo
2. Say if web search is needed and why
3. If searching: return test-relevant facts only (admin paths, hooks, multisite, limits)

Return External context playbook Step 1 + Step 4 format.
Do not write the test doc.
```

## Agent prompt — Web research (parallel, when approved)

```
Feature: {name}
Dependency: {plugin/service name}
Question: {specific test-design question}

Search official/developer documentation. Return:
- Source URLs
- Facts that change surfaces, contexts, selectors, or Not automated
- Unknowns still needing manual QA
```

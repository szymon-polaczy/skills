# Doc template

Write `THEME/test_docs/{feature-slug}.md`. Match the tone of any existing human-readable test doc in the project if one exists — otherwise use short `Note:` lines, imperative bullet steps, and explicit expectations.

Only include optional sections (test data setup, shared login steps, global assumptions) when discovery or an existing project doc shows they are needed for this feature.

---

```markdown
# {Feature Title}

Cypress spec: `{relative-path-from-THEME-to-spec}/{feature-slug}.cy.js`

**Scope & discovery summary**
- **Theme:** {theme name / path}
- **Surfaces:** {every entry point — pages, modals, options screens, embeds — not just one URL}
- **Contexts:** {sites, roles, scopes where behavior differs}
- **Code files:** {key files touched}
- **Config / options:** {plugins, fields, options, IDs — only what applies}
- **URLs touched:** {count across all surfaces × contexts}
- **Preconditions:** {auth, cart, role, locale — only what applies}
- **Not automated:** {backend, email, webhooks — only what applies}

**External dependencies** *(only if feature touches plugins/services outside THEME)*
- **{Name}:** {role in feature}
  - Docs consulted: {local path or URL}
  - Affects tests: {surfaces, setup, limits}

### Coverage matrix

| Surface \ Context | {Context A} | {Context B} |
|-------------------|-------------|-------------|
| {Surface 1}       | works       | hidden      |
| {Surface 2}       | works       | different   |

**Intentional omissions**
| Cell | Reason |
|------|--------|
| … | … |

Every **works**, **hidden**, and **different** cell must have a matching test case below or a row here.

---

## {Test group name}

### {Test case title}

Note: {context, dependencies, known flakiness — omit if obvious}

- {action step}
- expect {assertion}

### {Test case with multiple URLs}

Note: ...

- paths to check
	- `base_url/{path}/`
	- `base_url/{other-path}/`
- visit each path
- expect {assertion per path or shared assertion}

---

## {Another test group}

...
```

---

## Conventions

| Element | Rule |
|---------|------|
| `base_url` | Placeholder for Cypress `baseUrl` — no hardcoded domains |
| `###` headings | One test case each → maps 1:1 to a Cypress `it(...)` |
| Coverage matrix | Required — see [coverage-playbook.md](coverage-playbook.md) |
| Surfaces | Group tests by surface or context; include **negative** cases where feature is absent |
| `paths to check` | Use when same assertion applies across multiple contexts — list all paths, do not pick one |
| `Note:` | Admin/config deps, timing/cache warnings, manual-only gaps |
| Steps | Imperative: “go to”, “click”, “fill in”, “expect” |
| Paths | Match how the site uses slashes (discover from live URLs or existing tests) |
| Fields | Prefer label/placeholder text over HTML `name` attributes |
| Selectors | Stable classes or data attributes from discovery |
| Not automated | Call out backend side effects Cypress cannot verify |

## Optional sections (include only when relevant)

Add these **between the summary and the first test group** when discovery shows they apply. Do not add empty placeholders.

### Test data / environment setup

When tests depend on specific CMS content, options, or seeded data:

```markdown
**Test data setup**
Configure before running (or update paths/values in this doc):
- {what to configure} → {expected effect}
```

### Shared preconditions

When many tests share the same setup (login, cart, cookie state):

```markdown
**Shared setup: {name}**
- {steps once, referenced by test groups below}
```

### Project-wide assumptions

When an existing project test doc defines rules that apply to this feature (form-filling style, link checks, auth flow), copy **only the relevant bullets** — do not paste unrelated project-specific rules (multisite, shop pairs, etc.) unless this feature uses them.

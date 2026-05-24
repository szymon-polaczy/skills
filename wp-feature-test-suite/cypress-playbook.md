# Cypress playbook

Implement tests only **after** the user approves `THEME/test_docs/{feature-slug}.md`.

Optional speed-up: launch two readonly `explore` agents in one message before writing — one reads existing specs for style, one reads support modules — then implement sequentially.

## 1 — Resolve paths (same as SKILL.md)

From the theme’s `cypress.config.js`:

- `SPEC_DIR` — where `{feature-slug}.cy.js` goes
- `SUPPORT_DIR` — existing custom commands
- `CYPRESS_CWD` — where to run npm scripts
- `baseUrl`

Do not hardcode `resources/` or `inc/` — use whatever this theme’s config defines.

## 2 — Read before writing

Before creating files, read:

- The approved test doc
- `SUPPORT_DIR/e2e.js` and any required submodules
- One existing spec in `SPEC_DIR` for describe/it style, isolation, afterEach patterns
- Existing helper modules (form helpers, auth, site-specific commands)

Reuse commands that already exist. Extend; do not fork duplicate login or form-fill logic.

## 3 — Spec skeleton

```javascript
/// <reference types="cypress" />

/**
 * {Feature Title}
 *
 * Spec: test_docs/{feature-slug}.md
 */
const { /* named exports from existing config */ } = require('../support/...');

describe('{Feature Title}', { testIsolation: false }, () => {
  describe('{Test group from doc}', () => {
    it('{test case title from ### heading — lowercase}', () => {
      // steps from doc bullets
    });
  });
});
```

Adjust `require` depth to match where the spec lives relative to support.

## 4 — Doc → code mapping

| Doc element | Cypress |
|-------------|---------|
| Coverage matrix cell **works** | At least one test visiting that surface in that context |
| Coverage matrix cell **hidden** | Negative test — expect UI absent or access denied |
| Coverage matrix cell **different** | Test with context-specific assertion |
| `### Test case title` | `it('test case title — lowercase', ...)` |
| `- go to base_url/...` | `cy.visit('/...')` |
| `- expect status code N` | `cy.request({ followRedirect: false })` or visit + assert |
| `- fill in {Label}` | label-based helpers if available; else `cy.fillFieldByLabel` pattern |
| `- click on {selector}` | `cy.get(...).click()` |
| `- wait until page reloads` | `cy.url()` change or visible success element |
| `Note:` with config/data deps | comment in spec + constant in shared config if reused |
| `paths to check` + loop | `cy.wrap(paths).each(...)` — implement **all** listed paths, not one representative |
| `Not automated` | skip — no empty placeholder tests |

## 5 — Helpers and config

| Need | Action |
|------|--------|
| Path used 2+ times | Add to existing support config module |
| Multi-step flow reused | `SUPPORT_DIR/.../{feature-slug}-helpers.js` + register from support entry |
| One-off assertion | Keep inline in spec |

Name commands after behavior: `cy.submitSupportRequest()`, not `cy.testCase3()`.

## 6 — Auth, captcha, staging

Follow patterns already in the theme’s support layer:

- Guest reset: clear cookies/storage if the project has `becomeGuest` or equivalent
- Login: env credentials (`Cypress.env(...)`) — never hardcode secrets
- Turnstile/captcha: wait for response field before submit if the project does this
- Basic auth: use overwritten `visit`/`request` if present in `e2e.js`

## 7 — Project-specific helpers

If the test doc or existing specs define extra assertions (link checks, path prefixes, locale pairs, etc.):

- Reuse the project’s existing support commands and config — do not recreate them
- Add `afterEach` hooks only when comparable existing specs do

## 8 — testIsolation

Match neighboring specs:

- `{ testIsolation: false }` on describe when session must carry (login flows)
- Clear guest state in dedicated tests that require it

## 9 — Running

From `CYPRESS_CWD`:

```bash
npm run cypress:run -- --spec {path-to-spec-relative-to-CWD}
```

If the theme uses a root wrapper config, run from theme root and pass the resolved absolute or configured spec path.

Requires env vars the project already expects (basic auth, test user, etc.).

## 10 — Do not

- Edit the approved test doc during implementation unless a discovery error is found — then stop and ask
- Add tests for “Not automated” backend behavior
- Create a parallel Cypress folder structure — stay inside this theme’s existing layout
- Merge into a monolithic legacy test doc unless the user asks

---
name: add-security-packages
description: >-
  Add Semgrep (SAST) and Snyk Open Source (SCA) to a project with local npm/shell
  scripts, GitHub PR workflows (both checks, diff-aware SAST), deploy SCA gates,
  and skippable hotfix bypasses. Use when the user asks to add security scanning,
  SAST, SCA, Semgrep, Snyk, /add_security_packages, security CI, dependency
  vulnerability checks, or harden GitHub workflows with security gates.
---

# Add security packages (Semgrep + Snyk)

## User intent (default scope)

When invoked (e.g. `/add_security_packages`), implement:

> Add SAST and SCA tools to the project. They need to be setup to be easily run locally, by me or an AI agent while working, but they also need to be added to the .github flows. When a PR is created the changes inside need to be checked to make sure they are up to the standards, for this we need to setup both SCA and SAST tools to run. For deployment flow we need to just setup SCA to check the packages before installing them. Both of these should be able to be skipped if a user requires it, so that any hot fixes for production can be quickly deployed with checks ran afterwards.
>
> SAST tool of choice: Semgrep for PHP, WordPress, and JS/TS/Vue.
> SCA tool of choice: Snyk Open Source CLI.

---

## Phase 0: Check CLI tools (always first)

**Before discovery or implementation**, verify both CLIs are on `PATH`:

```bash
command -v semgrep && semgrep --version
command -v snyk && snyk --version
```

| Result | Action |
|--------|--------|
| Both found | Continue to Phase 1. Optionally verify `snyk auth` / API access with `snyk test --help` — if unauthenticated, remind user to run `snyk auth`. |
| Either missing | **Stop.** Tell the user which binary is missing and ask them to install before proceeding. Do not write project config until CLIs work locally. |

Install commands (macOS Homebrew; adapt for Linux/Windows):

```bash
brew install semgrep
brew install snyk-cli
snyk auth   # one-time; stores token locally
```

**Tools are not npm packages** — do not add `semgrep` or `snyk` as npm devDependencies unless the user explicitly asks. CI installs Snyk via `npm install -g snyk` or uses the official action; Semgrep runs via `semgrep/semgrep-action` or `pip install semgrep`.

CI uses `SNYK_TOKEN` repository secret. Semgrep needs no token for community registry rules.

---

## Snyk vs Semgrep (do not conflate)

| | **Snyk (SCA)** | **Semgrep (SAST)** |
|---|---|---|
| Scans | Lockfiles / manifests (`package-lock.json`, `composer.lock`, …) | First-party source code |
| Finds | Known CVEs in dependencies | Unsafe code patterns (XSS, injection, …) |
| Never finds | Bugs in your own code | Vulnerabilities inside `node_modules` / vendor |

Zero Semgrep findings does **not** mean dependencies are safe. Many Snyk findings does **not** mean Semgrep is broken.

---

## Phase 1: Discover the repo

Before writing config, map:

1. **Git root(s)** — monorepo vs multiple repos (repeat setup per repo).

2. **Dependency roots (SCA)** — search the **entire repo** for every manifest/lock pair. Do not assume a single root.

   ```bash
   # Find candidates (adjust depth/globs as needed)
   find . -name 'package.json' -not -path '*/node_modules/*'
   find . -name 'package-lock.json' -not -path '*/node_modules/*'
   find . -name 'composer.json' -not -path '*/vendor/*'
   find . -name 'composer.lock' -not -path '*/vendor/*'
   ```

   Check **all** common locations:
   - Repository root (Node apps, Bedrock-style WordPress with root `composer.json`)
   - Theme/build package (e.g. `web/app/themes/*/`, `themes/*/` with its own `package.json`)
   - Custom plugins/mu-plugins that ship their own `composer.json`
   - Bedrock / Composer-managed WP: root `composer.json` + `composer.lock` is often the primary SCA target alongside theme npm

   Rules:
   - **npm**: each `package-lock.json` (or yarn/pnpm lock) → one `snyk test` target
   - **composer**: each `composer.lock` → one `snyk test --file=…/composer.lock --package-manager=composer` (never `.json` — see Phase 4)
   - Skip lockfiles under `node_modules/`, `vendor/`, or third-party plugin trees unless the user says otherwise
   - If `composer.json` exists without `composer.lock`, generate the lock before adding Snyk (Phase 4)

3. **First-party code paths (SAST)** — ask the user to confirm scope:

   - **Ask the user**: “Which custom/first-party plugins, mu-plugins, or packages should be included in Semgrep? List paths that are yours — exclude external/vendor plugins (Yoast, ACF Pro, etc.).”
   - Do not guess third-party vs custom; present a candidate list from `plugins/`, `mu-plugins/`, `themes/` and let the user mark first-party paths.
   - Always exclude: `vendor/`, `node_modules/`, build output (`.nuxt`, `dist`, `.output`), and paths the user marks as external.

4. **Existing CI** — PR triggers, deploy workflows, runner type (GitHub-hosted vs self-hosted).

5. **Primary entry point for local runs** — root `package.json`, theme `package.json`, or a small `scripts/security/` wrapper; pick one place for `npm run security` that can reach all SCA roots and SAST paths.

Record findings in a short checklist before implementing. **Do not implement until dependency roots and first-party paths are confirmed with the user** (especially on WordPress / Bedrock repos).

---

## Phase 2: Local scripts

### npm project (single root)

Add to `package.json`:

```json
"security:sast": "semgrep scan --config p/default --config p/typescript --config p/security-audit --config p/owasp-top-ten",
"security:sast:ci": "semgrep scan --config p/default --config p/typescript --config p/security-audit --config p/owasp-top-ten --error",
"security:sca": "snyk test --severity-threshold=high",
"security": "npm run security:sca && npm run security:sast"
```

- `security:sast` — informational locally (no `--error`).
- `security:sast:ci` — fails on findings; use in CI or before merge.
- `security:sca` — run from directory containing the lockfile.

### Multi-root / sub-package entry (e.g. WordPress theme + composer plugin)

Centralize in the most natural `package.json` and scan upward:

```json
"security:sast": "semgrep scan --config p/default --config p/php --config p/wordpress --config p/security-audit --error . ../other-first-party-dir",
"security:sca:app": "snyk test --severity-threshold=high",
"security:sca:other": "snyk test --file=../path/to/composer.lock --package-manager=composer --severity-threshold=high"
```

> **Composer:** always use `composer.lock` in `--file`, never `composer.json` — Snyk treats `--file` as a lockfile and fails with “Must contain `packages` property” if given a manifest.

```json
"security:sca": "npm run security:sca:app && npm run security:sca:other",
"security": "npm run security:sca && npm run security:sast"
```

Add `scripts/security/README.md` documenting: prerequisites, commands, skip mechanism, Snyk vs Semgrep.

---

## Phase 3: Semgrep rulesets (critical pitfalls)

### Registry packs go on the CLI, not in `.semgrep.yml` `rules:`

**Wrong** — causes `Invalid rule schema` / `'p/security-audit' is not of type 'object'`:

```yaml
rules:
  - p/javascript
  - p/security-audit
```

**Right** — multiple `--config` flags:

```bash
semgrep scan --config p/default --config p/php --config p/wordpress --config p/security-audit
```

Do **not** use a paths-only `.semgrep.yml` without a `rules:` section — Semgrep rejects it (`One of these properties is missing: 'rules'`). Use **`.semgrepignore`** for exclusions instead.

There is **no** `p/vue` registry pack. **`p/javascript` and `p/typescript` do not scan `.vue` files** (0 targets). Always include **`p/default`** for Vue/Nuxt/SFC projects — it enables `javascript.vue.*` rules.

### Recommended packs by stack

| Stack | Semgrep `--config` packs |
|-------|--------------------------|
| JS/TS/Node | `p/default`, `p/typescript`, `p/security-audit`, `p/owasp-top-ten` |
| Vue/Nuxt | **must include `p/default`** (see above) |
| PHP | `p/php`, `p/security-audit` |
| WordPress (first-party) | `p/wordpress`, `p/php`, `p/default`, `p/security-audit` |

Pass explicit scan targets for scoped scans:

```bash
semgrep scan --config p/default ... --error ./src ../mu-plugins/my-plugin
```

WordPress: exclude third-party plugins in `.semgrepignore`; scan only paths the user confirmed as first-party.

Triage Semgrep findings before enabling `--error` in CI — some rules flag intentional patterns (e.g. framework-specific APIs, trusted rich text). Use `.snyk` / Semgrep rule overrides for accepted risks.

---

## Phase 4: Snyk SCA (critical pitfalls)

### Always point Composer scans at the lockfile

**Wrong** — Snyk parses `composer.json` as a lock file:

```bash
snyk test --file=path/to/composer.json --package-manager=composer
# Error: Invalid lock file. Must contain `packages` property
```

**Right**:

```bash
snyk test --file=path/to/composer.lock --package-manager=composer --severity-threshold=high
```

For npm, run `snyk test` from the directory with `package-lock.json` (or `--file=package-lock.json`).

### Composer lock missing

If `composer.json` exists but no lock:

1. Add path repository / version if needed for local packages.
2. Run `composer update --no-install` in that directory.
3. Commit `composer.lock`.

Use `snyk test` (not `snyk monitor`) in CI so PRs fail without Snyk project linking.

Default failure threshold: `--severity-threshold=high`.

Optional `.snyk` policy file for documented ignores.

---

## Phase 5: Skip mechanism (hotfixes)

Create `.github/actions/should-skip-security/action.yml` — see [templates.md](templates.md).

| Trigger | Effect |
|---------|--------|
| PR label `skip-security-checks` | Skip SAST + SCA on PR |
| PR label `skip-sast` / `skip-sca` | Skip one check on PR |
| Commit message `[skip-security]` | Skip both (PR + deploy) |
| Commit message `[skip-sca]` | Skip SCA (PR + deploy) |
| Commit message `[skip-sast]` | Skip SAST (PR only) |
| Deploy `workflow_dispatch` input `skip_sca: true` | Skip deploy SCA |

Composite action must read commit message via `git log -1` after checkout (PR events lack `head_commit.message`).

---

## Phase 6: GitHub workflows

### PR workflow — `.github/workflows/security-pr.yml`

- **Trigger**: `pull_request` → `main`, `staging` (adjust branches to project).
- **Runner**: `ubuntu-latest` for security (avoid requiring Semgrep/Snyk on self-hosted deploy runners).
- **Jobs**: `skip-check` → parallel `sast` + `sca`.
- **SAST**: `semgrep/semgrep-action@v1` with registry configs; set `SEMGREP_BASELINE_REF: ${{ github.event.pull_request.base.sha }}` for diff-only findings on changed lines.
- **SCA**: `npm install -g snyk`, `SNYK_TOKEN`, run all dependency roots (delegate to `npm run security:sca` when possible).

### Deploy workflows — SCA only, before `npm install`

Insert after checkout + skip check, before install:

```yaml
- uses: actions/setup-node@v4
  if: steps.skip_sca.outputs.skip_sca != 'true'
  with:
    node-version: '20'
    cache: npm
- run: npm install -g snyk
  if: steps.skip_sca.outputs.skip_sca != 'true'
- run: npm run security:sca
  if: steps.skip_sca.outputs.skip_sca != 'true'
  working-directory: path/to/package-with-scripts
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

Add `workflow_dispatch` input `skip_sca` to deploy workflows that lack it.

Do **not** add Semgrep to deploy (SCA only per requirements).

Full workflow templates: [templates.md](templates.md).

---

## Phase 7: Post-setup (tell the user)

1. Add `SNYK_TOKEN` secret to each GitHub repo.
2. Confirm local CLIs work (`semgrep --version`, `snyk --version`) and run `snyk auth` if not done.
3. Run `npm run security` (or project equivalent) to establish baselines.
4. Triage findings; add `.snyk` ignores or fix code before branch protection.
5. Optionally require `security-pr` checks on protected branches.

---

## Implementation checklist

Copy and track:

```
- [ ] Phase 0: semgrep + snyk CLI available locally (or user installing)
- [ ] Searched repo for all package.json / composer.json / lockfiles (root + theme + plugins)
- [ ] User confirmed first-party plugin/theme paths for SAST
- [ ] Mapped dependency roots (npm/composer/…)
- [ ] composer.lock committed where needed
- [ ] .semgrepignore scoped to first-party code
- [ ] Semgrep uses CLI --config packs (p/default for Vue)
- [ ] Snyk composer uses .lock not .json
- [ ] npm run security / security:sast / security:sca scripts
- [ ] scripts/security/README.md
- [ ] should-skip-security composite action
- [ ] security-pr.yml (SAST + SCA, baseline ref)
- [ ] Deploy workflows: SCA gate + skip_sca dispatch
- [ ] SNYK_TOKEN documented
```

---

## Verification

After implementation, confirm:

1. `npm run security:sast` — scan summary shows expected file counts; Vue projects show `javascript.vue.*` rules when using `p/default`.
2. `npm run security:sca` — Snyk reports dependency vulns (not lock-file schema errors).
3. Semgrep with only `p/javascript` on a `.vue` file → **0 targets** = misconfigured; add `p/default`.
4. Dry-run skip: commit message `[skip-sca]` should skip SCA in composite action output.

---

## Additional resources

- Copy-paste templates: [templates.md](templates.md)

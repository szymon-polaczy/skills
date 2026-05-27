# Security setup templates

Copy and adapt paths, Node versions, and branch names to the project.

---

## `.github/actions/should-skip-security/action.yml`

```yaml
name: Should skip security checks
description: Determines whether SAST and/or SCA should be skipped based on labels, commit messages, and dispatch inputs.

outputs:
  skip_sast:
    description: Whether to skip Semgrep SAST
    value: ${{ steps.evaluate.outputs.skip_sast }}
  skip_sca:
    description: Whether to skip Snyk SCA
    value: ${{ steps.evaluate.outputs.skip_sca }}

runs:
  using: composite
  steps:
    - name: Evaluate skip conditions
      id: evaluate
      shell: bash
      env:
        HEAD_COMMIT_MESSAGE: ${{ github.event.head_commit.message || '' }}
        DISPATCH_SKIP_SCA: ${{ github.event.inputs.skip_sca || 'false' }}
        PR_LABELS: ${{ toJSON(github.event.pull_request.labels.*.name) }}
      run: |
        skip_sast=false
        skip_sca=false

        COMMIT_MESSAGE="$HEAD_COMMIT_MESSAGE"
        if [ -d .git ]; then
          COMMIT_MESSAGE="$(git log -1 --format=%B 2>/dev/null || echo "$COMMIT_MESSAGE")"
        fi

        if [[ "$COMMIT_MESSAGE" == *"[skip-security]"* ]]; then
          skip_sast=true
          skip_sca=true
        fi
        if [[ "$COMMIT_MESSAGE" == *"[skip-sast]"* ]]; then
          skip_sast=true
        fi
        if [[ "$COMMIT_MESSAGE" == *"[skip-sca]"* ]]; then
          skip_sca=true
        fi
        if [[ "$DISPATCH_SKIP_SCA" == "true" ]]; then
          skip_sca=true
        fi
        if echo "$PR_LABELS" | grep -q 'skip-security-checks'; then
          skip_sast=true
          skip_sca=true
        fi
        if echo "$PR_LABELS" | grep -q 'skip-sast'; then
          skip_sast=true
        fi
        if echo "$PR_LABELS" | grep -q 'skip-sca'; then
          skip_sca=true
        fi

        echo "skip_sast=$skip_sast" >> "$GITHUB_OUTPUT"
        echo "skip_sca=$skip_sca" >> "$GITHUB_OUTPUT"
        echo "skip_sast=$skip_sast skip_sca=$skip_sca"
```

---

## `.github/workflows/security-pr.yml`

```yaml
name: Security PR checks

on:
  pull_request:
    branches:
      - main
      - staging

permissions:
  contents: read
  pull-requests: read

jobs:
  skip-check:
    runs-on: ubuntu-latest
    outputs:
      skip_sast: ${{ steps.skip.outputs.skip_sast }}
      skip_sca: ${{ steps.skip.outputs.skip_sca }}
    steps:
      - uses: actions/checkout@v4
      - id: skip
        uses: ./.github/actions/should-skip-security

  sast:
    name: SAST (Semgrep)
    needs: skip-check
    if: needs.skip-check.outputs.skip_sast != 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/default
            p/typescript
            p/security-audit
            p/owasp-top-ten
        env:
          SEMGREP_BASELINE_REF: ${{ github.event.pull_request.base.sha }}

  sca:
    name: SCA (Snyk)
    needs: skip-check
    if: needs.skip-check.outputs.skip_sca != 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
      - run: npm install -g snyk
      - name: Snyk test
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        run: npm run security:sca
        working-directory: .   # or sub-package path
```

**WordPress / PHP variant** — SAST job:

```yaml
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
          cache-dependency-path: path/to/theme/package-lock.json
      - run: pip install semgrep
      - run: npm run security:sast
        working-directory: path/to/theme
        env:
          SEMGREP_BASELINE_REF: ${{ github.event.pull_request.base.sha }}
```

Semgrep registry configs for WP SAST (in `security:sast` script):

```
p/default p/php p/wordpress p/security-audit
```

---

## Deploy workflow — SCA gate snippet

Add to existing deploy job **before** `npm install`:

```yaml
  workflow_dispatch:
    inputs:
      skip_sca:
        description: 'Skip Snyk SCA before install (hotfix deploys)'
        required: false
        type: boolean
        default: false

# steps:
      - uses: actions/checkout@v4

      - id: skip_sca
        uses: ./.github/actions/should-skip-security

      - uses: actions/setup-node@v4
        if: steps.skip_sca.outputs.skip_sca != 'true'
        with:
          node-version: '20'
          cache: npm

      - run: npm install -g snyk
        if: steps.skip_sca.outputs.skip_sca != 'true'

      - name: SCA - Snyk
        if: steps.skip_sca.outputs.skip_sca != 'true'
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        run: npm run security:sca
        working-directory: .

      - name: Install dependencies
        run: npm ci
```

---

## `.semgrepignore` (example)

```
node_modules/
.nuxt/
.output/
dist/
**/vendor/
**/acf-json/
# third-party paths — project-specific
```

---

## `.snyk` (starter policy)

```yaml
# Document accepted risks: snyk ignore --expiry=YYYY-MM-DD --reason='...'
version: v1.25.0
ignore: {}
```

---

## Snyk commands by package manager

```bash
# npm (from lockfile directory)
snyk test --severity-threshold=high

# npm (explicit lockfile)
snyk test --file=package-lock.json --severity-threshold=high

# Composer — MUST use lockfile (.json as --file causes "Must contain packages property" error)
snyk test --file=path/to/composer.lock --package-manager=composer --severity-threshold=high

# Multiple roots
npm run security:sca:app && npm run security:sca:other
```

---

## `scripts/security/README.md` (outline)

```markdown
# Security scanning

## Snyk vs Semgrep
| Tool | Finds | Does not find |
| Snyk | Dependency CVEs | Your source-code bugs |
| Semgrep | Code patterns in your code | node_modules CVEs |

## Prerequisites
brew install semgrep snyk-cli
snyk auth
Add SNYK_TOKEN to GitHub repo secrets.

## Run locally
npm run security
npm run security:sca
npm run security:sast
npm run security:sast:ci   # strict / CI-equivalent

## Skipping (hotfixes)
| PR label skip-security-checks | Skip both |
| [skip-sca] in commit | Skip SCA |
| workflow_dispatch skip_sca: true | Skip deploy SCA |
```

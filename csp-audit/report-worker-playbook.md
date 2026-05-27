# Batch triage (master in-process)

**Default triage method.** No Task tool. No browser. No files per issue.

---

## Input (from queue line)

```text
- [ ] https://glitch.../issues/15755/ | connect-src | https://psx4.linkedin.com
```

## Output (same line, marked done)

```text
- [x] https://glitch.../issues/15755/ | connect-src | https://psx4.linkedin.com — **added** — add connect-src https://psx4.linkedin.com LinkedIn pixel shard
```

---

## Batch loop

```
remaining = lines matching "^- \[ \]"
while remaining:
  take first 25
  for each line: verdict + one-line why (use CSP excerpt + rules below)
  write back as [x]
```

One model turn should process all 25 — do not spawn subagents per URL.

---

## Post-deploy triage (mandatory)

**All queue issues = after last CSP deploy.** Matching the excerpt does **not** close the item.

### Verdict decision tree

1. **skipped** — attack/junk only (see below). Not “vendor we use but annoying.”
2. **added** — legit vendor; blocked host **not** in CSP excerpt for **that directive** (exact origin or wildcard that actually matches the host per CSP3 rules).
3. **required more research** — everything else that is not skip, including:
   - Host **is** in excerpt (exact or wildcard) but GlitchTip still shows the issue → **always** research (redirect, wrong directive, `img-src` vs `connect-src`, pre-redirect reporting, stale cache — do not mark “covered”)
   - Parent brand in CSP but host differs (`google.com` vs `google.de`, `psx` vs `psx4`) → research with mismatch type in one line
   - `*.google.com` does **not** cover `google.co.uk` → **added** if truly missing; **required more research** if `google.com` literal exists but TLD variant reports

**Forbidden in Pass 1:** verdicts like “already covered”, “no change”, “CSP has this host — done”. Those belong in Pass 2 after vendor/redirect investigation.

### CSP excerpt match (for routing only — not closure)

Use excerpt only to choose **added** vs **required more research**:

| Excerpt | Post-deploy report | Pass 1 verdict |
|---------|-------------------|----------------|
| No match for directive | Legit vendor | **added** |
| Match (exact or wildcard) | Still in GlitchTip | **required more research** — “in CSP, still reporting” |
| Partial parent only | Still in GlitchTip | **required more research** — note mismatch type |

---

## Skip signals (no allowlist)

- Typosquat of known vendor
- Random `.xyz` / crypto / paste domains
- `javascript:` / `data:` in blocked-uri
- No connection to project vendors from code search

---

## After Pass 1 batches

Group all **added** by directive → **one** config edit. Write **Skipped** to `csp.md`.

If any **required more research** lines exist → **do not hand off** — run Pass 2 ([vendor-research-playbook.md](vendor-research-playbook.md)) automatically.

---

## Pass 1 vs Pass 2 verdicts

| Pass | Verdicts |
|------|----------|
| 1 | added, skipped, required more research |
| 2 | Re-tag research → **monitor** (vendor/redirect) or keep **required more research** (architectural) |

**required more research** in Pass 1 means "defer to vendor research" — not "ask the user."

---

## Deprecated: per-issue workers

The old flow (Task + browser per URL) is **deprecated**. If an agent starts launching Task workers for each issue, stop and use this batch flow instead.

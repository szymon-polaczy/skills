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

## CSP match check (for "required more research")

Blocked host already covered if CSP excerpt contains any of:

- Exact origin `https://host`
- Wildcard covering host (`*.linkedin.com` covers `psx4.linkedin.com`)
- **Not** covered: `*.google.com` does **not** cover `google.co.uk` → that's **added** or **required more research** if `google.com` literal exists

When parent brand is in CSP but host differs (google.com vs google.de, psx vs psx4) → **required more research** with one line noting mismatch type.

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

---
name: csp-audit
description: >-
  Two-pass CSP audit: bulk-scrape GlitchTip, batch triage (added|skipped|required
  more research), apply CSP edits, then automatic vendor research pass (wildcards,
  redirect patterns, official CSP docs) and second CSP update. User gets one final
  handoff with optional security tradeoffs to review. Use for CSP or GlitchTip reports.
disable-model-invocation: true
---

# CSP Audit (GlitchTip) — two-pass, one handoff

**Pass 1:** scrape → triage → apply **added**  
**Pass 2:** research all **required more research** → vendor wildcards → apply → re-tag → **one final message to user**

User is **not** asked mid-run ("which would you prefer?"). Tradeoffs go in `csp.md` for review at the end.

Read when needed:
- [glitchtip-playbook.md](glitchtip-playbook.md) — bulk list scrape
- [report-worker-playbook.md](report-worker-playbook.md) — batch triage (25/turn)
- [vendor-research-playbook.md](vendor-research-playbook.md) — **Pass 2 (automatic)**
- [discovery-playbook.md](discovery-playbook.md) — find CSP in code

---

## Verdicts

### Pass 1

| Verdict | Action |
|---------|--------|
| **added** | Missing legit origin → collect for Pass 1 CSP edit |
| **skipped** | Attack/junk/unwanted |
| **required more research** | Looks in CSP already, or weird — **defer to Pass 2** |

### Pass 2 (re-tag research items)

| Verdict | Meaning |
|---------|---------|
| **monitor** | Vendor wildcard applied or already covered; re-check GlitchTip after deploy |
| **required more research** | Architectural only (frame-ancestors, script-src-attr, strict-dynamic) |

---

## Pass 1 — Fast triage

1. CSP baseline → `csp.md` + excerpt
2. Bulk scrape list → `csp-reports-queue.md` as `url | directive | blocked-uri`
3. Batch triage 25/turn — **no subagents, no per-issue browser**
4. **One** CSP edit for all **added** (dedupe)
5. Write Skipped to `csp.md` — **do not** hand off yet if any **required more research** exist

---

## Pass 2 — Vendor research (automatic)

If Pass 1 produced **any** `required more research` lines → **always run Pass 2** before handoff.

Follow [vendor-research-playbook.md](vendor-research-playbook.md):

1. Group research URLs by vendor (Google, LinkedIn, Bing, OneTrust, Adobe, …)
2. **One web search per vendor** — official CSP docs
3. Second CSP edit:
   - **Explicit + wildcard pair** (canonical host, then `*.` below)
   - Prefer `*` over hardcoded one-offs per vendor guidance
   - Known redirects → **monitor**, not new host
   - country TLD allowlist (e.g. `googleCountryTldList` in config) stays — no TLD wildcard shortcut
4. Re-tag queue: vendor items → **monitor**; architectural → stay **required more research**
5. Update `csp.md`: Pass 2 changelog, vendor links, Monitor, Security tradeoffs, Architectural

**Do not stop and ask the user** between Pass 1 and Pass 2.

---

## Final handoff (only message user needs)

After Pass 2:

```text
Pass 1: {added} added, {skipped} skipped
Pass 2: vendor wildcards applied; {monitor} monitor, {arch} architectural
Files: nuxt.config.js, csp.md, csp-reports-queue.md
Review: csp.md → Security tradeoffs (accept or narrow after deploy)
Deploy → re-check GlitchTip; monitor items may still report (redirect noise)
```

No per-issue essays. No "want me to implement X?" — already implemented.

---

## Speed rules

- List scrape only (no per-issue browser) in Pass 1
- Triage 25 lines/turn in master context
- Pass 2: group by vendor, max ~5 web searches total
- **Two** CSP config edits total (Pass 1 + Pass 2), **two** `csp.md` writes

---

## Checklist

```
Pass 1
- [ ] Queue complete with added/skipped/required more research
- [ ] First CSP edit applied

Pass 2 (if any required more research)
- [ ] Vendor docs consulted (batched)
- [ ] Wildcard hardening applied
- [ ] Queue re-tagged (monitor / architectural)
- [ ] csp.md: tradeoffs + monitor + architectural

Handoff
- [ ] Single summary — user not prompted mid-run
```

---
name: csp-audit
description: >-
  Two-pass CSP audit assuming all GlitchTip issues are post-deploy: scrape CSP-only
  URL as-is, triage (added only if missing from CSP; in-CSP-but-reporting → required
  more research), apply edits, then automatic vendor research for persistent reports.
  Never close as "already covered." Use for CSP or GlitchTip reports.
disable-model-invocation: true
---

# CSP Audit (GlitchTip) — two-pass, one handoff

**Pass 1:** scrape → triage → apply **added**  
**Pass 2:** research all **required more research** → vendor wildcards → apply → re-tag → **one final message to user**

User is **not** asked mid-run ("which would you prefer?"). Tradeoffs go in `csp.md` for review at the end.

## Post-deploy baseline (mandatory)

**Assume every issue in the GlitchTip queue appeared after the last CSP deployment.** The list is live production signal, not a backlog from before fixes shipped.

| Wrong | Right |
|-------|-------|
| “Host is in CSP → no work” | Host in CSP but still reporting → **required more research** (Pass 1), then Pass 2 |
| Close audit because allowlist “looks complete” | Investigate why reports persist post-deploy (redirect, wrong directive, `img-src` gap, wildcard limits, architectural) |
| Skip Pass 2 for “already covered” lines | **All** covered-but-reporting lines go through Pass 2 |

**Pass 1 `added`** only when the blocked origin is **genuinely missing** from the CSP excerpt for that directive.  
**Pass 1 `required more research`** when the host **matches** the excerpt (exact or wildcard) *or* parent brand is partially there — persistence after deploy means the current policy is not sufficient, not that triage is done.

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
| **added** | Legit vendor; origin **absent** from CSP excerpt for that directive → Pass 1 CSP edit |
| **skipped** | Attack/junk/unwanted only |
| **required more research** | Origin **present** in excerpt but still reporting post-deploy; partial parent match; or weird — **always Pass 2** |

### Pass 2 (re-tag research items)

| Verdict | Meaning |
|---------|---------|
| **monitor** | Pass 2 investigated post-deploy persistence; fix applied or documented redirect/vendor noise — **not** “was in CSP so ignore” |
| **required more research** | Architectural only (frame-ancestors, script-src-attr, strict-dynamic) |

---

## GlitchTip URL (user-provided)

The user’s GlitchTip link is already a **CSP-only project or saved view** (every issue is a CSP violation). Treat it as the complete filter.

| Do | Do not |
|----|--------|
| `browser_navigate` to the URL **exactly** as given | Type in the GlitchTip **search bar** |
| Scrape the issues list from that page | Add queries like `is:unresolved Content Security Policy violation` |
| Keep existing URL query params if present | Append `query=`, `search=`, or Sentry-style CSP text filters |

If the page shows a login form → user logs in once; **do not** re-filter after login.

---

## Pass 1 — Fast triage

1. CSP baseline → `csp.md` + excerpt
2. Bulk scrape list → `csp-reports-queue.md` as `url | directive | blocked-uri` (use GlitchTip URL rules above)
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
   - Known redirects → **monitor** only after documenting why reports persist post-deploy; not “already in CSP”
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

- List scrape only (no per-issue browser) in Pass 1; **no search-bar filtering** on GlitchTip
- Triage 25 lines/turn in master context
- Pass 2: group by vendor, max ~5 web searches total
- **Two** CSP config edits total (Pass 1 + Pass 2), **two** `csp.md` writes

---

## Checklist

```
Pass 1
- [ ] Post-deploy baseline applied (in-CSP lines → required more research, not "covered")
- [ ] GlitchTip scraped from user URL only (no search-bar CSP query)
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
